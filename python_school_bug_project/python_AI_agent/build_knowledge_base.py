from sentence_transformers import SentenceTransformer
import chromadb
import os
import docx # 导入 python-docx 库

# --- 配置 --- 
# 修改知识库源文件指向你的 .docx 文件
KNOWLEDGE_SOURCE_FILE = "./my_knowledge_collection/网络安全产品（V3.0）-5.15.docx" 
# 或者你可以配置一个文件夹，然后遍历其中的 .docx 文件
# KNOWLEDGE_SOURCE_DIR = "./my_knowledge_collection/"

CHROMA_DB_PATH = "./my_chroma_db"  # ChromaDB数据存储路径
COLLECTION_NAME = "my_knowledge_collection" # 知识库集合名称
# EMBEDDING_MODEL_NAME = 'E:\\python_project\\python_school_bug_project\\pythonProject\\local_m3e_base_model' # 指向你的本地模型文件夹

def load_documents_from_docx(file_path, chunk_size=800, overlap=200):
    """使用滑动窗口方式分割文档，保持上下文连贯性"""
    docs = []
    if os.path.exists(file_path) and file_path.endswith('.docx'):
        try:
            document = docx.Document(file_path)
            # 将所有段落合并成一个长文本
            paragraphs = [para.text.strip() for para in document.paragraphs if para.text.strip()]
            full_text = "\n".join(paragraphs)
            
            print(f"原始文档总长度: {len(full_text)} 字符")
            
            # 使用滑动窗口分割
            for i in range(0, len(full_text), chunk_size - overlap):
                chunk = full_text[i:i + chunk_size]
                if len(chunk.strip()) > 100:  # 只保留有意义的块
                    docs.append(chunk.strip())
            
            print(f"分割后得到 {len(docs)} 个文档块")
            for i, doc in enumerate(docs[:3]):  # 显示前3个块的预览
                print(f"块 {i+1} (长度: {len(doc)}): {doc[:100]}...")
                
        except Exception as e:
            print(f"Error loading docx file {file_path}: {e}")
    return docs

# 如果你希望从一个文件夹加载所有 .docx 文件
def load_all_docx_from_directory(dir_path):
    all_docs = []
    if os.path.isdir(dir_path):
        for filename in os.listdir(dir_path):
            if filename.endswith(".docx"):
                file_path = os.path.join(dir_path, filename)
                docs_from_file = load_documents_from_docx(file_path)
                all_docs.extend(docs_from_file)
        print(f"Loaded a total of {len(all_docs)} paragraphs from .docx files in {dir_path}")
    else:
        print(f"Warning: Knowledge source directory '{dir_path}' not found.")
    return all_docs


def main():
    # print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer("local_m3e_base_model")

    print(f"Initializing ChromaDB client at {CHROMA_DB_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    print(f"Getting or creating collection: {COLLECTION_NAME}...")
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        # 如果希望每次都清空并重建，可以取消下面的注释
        print(f"Collection '{COLLECTION_NAME}' exists. Deleting and recreating.")
        client.delete_collection(name=COLLECTION_NAME)
        collection = client.create_collection(name=COLLECTION_NAME)
    except:
        collection = client.create_collection(name=COLLECTION_NAME)

    print("Loading documents from source...")
    # 根据你的配置选择加载方式
    documents = load_documents_from_docx(KNOWLEDGE_SOURCE_FILE)
    # 或者，如果你配置了 KNOWLEDGE_SOURCE_DIR 并想加载目录下所有docx:
    # documents = load_all_docx_from_directory(KNOWLEDGE_SOURCE_DIR)

    if not documents:
        print("No documents to process. Exiting.")
        return

    print(f"Generating embeddings for {len(documents)} documents...")
    embeddings = model.encode(documents, show_progress_bar=True)

    ids = [f"doc_{i}" for i in range(len(documents))]

    print("Adding documents to ChromaDB...")
    batch_size = 166  # ChromaDB 的最大批量限制
    # 分批添加文档
    for i in range(0, len(documents), batch_size):
        batch_embeddings = embeddings[i:i+batch_size].tolist()
        batch_documents = documents[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_documents,
            ids=batch_ids
        )
    print(f"Successfully added/updated {collection.count()} documents in '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    main()