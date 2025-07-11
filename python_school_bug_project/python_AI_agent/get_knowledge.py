import chromadb
from sentence_transformers import SentenceTransformer

# 指向之前保存的数据库路径
CHROMA_DB_PATH = "./my_chroma_db"
COLLECTION_NAME = "my_knowledge_collection"

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(name=COLLECTION_NAME)

model = SentenceTransformer("local_m3e_base_model")

def query_knowledgebase(question, top_k=5):
    #top_k = 5: 可选参数，表示返回最相似的前5个结果。

    # 将用户问题也编码为向量
    embedding = model.encode([question]).tolist()

    # 在 ChromaDB 中搜索最相似的文档
    results = collection.query(query_embeddings=embedding, n_results=top_k)

    # 返回匹配的文档内容和距离（可选）
    return results["documents"][0], results["distances"][0]

def query_knowledgebase_detailed(question, top_k=5, min_length=30):
    """获取更详细的知识库内容"""
    # 将用户问题也编码为向量
    embedding = model.encode([question]).tolist()
    
    # 在 ChromaDB 中搜索最相似的文档
    results = collection.query(
        query_embeddings=embedding, 
        n_results=top_k,
        include=['documents', 'distances']  # 包含更多信息
    )
    
    print(f"检索到 {len(results['documents'][0])} 个文档片段")
    
    detailed_results = []
    for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0])):
        print(f"片段 {i+1}: 长度={len(doc)}, 相似度={dist:.2f}")
        print(f"内容预览: {doc[:100]}...")
        
        # 过滤掉太短的片段
        if len(doc) >= min_length:
            detailed_results.append({
                'content': doc,
                'similarity': dist,
                'length': len(doc)
            })
    
    return detailed_results

def get_knowledge_for_ai(question, max_context_length=2000):
    """为AI获取知识上下文，合并相关片段"""
    print(f"正在为问题检索知识: {question}")
    detailed_results = query_knowledgebase_detailed(question, top_k=10, min_length=30)
    
    print(f"过滤后得到 {len(detailed_results)} 个有效片段")
    
    # 按相似度排序并合并内容
    context_parts = []
    total_length = 0
    
    for i, result in enumerate(detailed_results):
        content = result['content']
        print(f"处理片段 {i+1}: 长度={len(content)}, 当前总长度={total_length}")
        
        if total_length + len(content) <= max_context_length:
            context_parts.append(f"[相似度: {result['similarity']:.2f}] {content}")
            total_length += len(content)
            print(f"添加片段 {i+1}, 新总长度={total_length}")
        else:
            print(f"片段 {i+1} 超出长度限制，跳过")
            continue
    
    final_context = "\n\n".join(context_parts)
    print(f"最终上下文长度: {len(final_context)}")
    print(f"最终上下文内容: {final_context[:200]}...")
    
    return final_context

if __name__ == "__main__":
    question = "NAT的配置方式"
    
    # 原始方法
    print("=== 原始检索结果 ===")
    # docs, distances = query_knowledgebase(question)
    # for doc, dist in zip(docs, distances):
    #     print(f"[相似度: {dist:.4f}] {doc}")
    
    print("\n=== 详细检索结果 ===")
    detailed_results = query_knowledgebase_detailed(question)
    for result in detailed_results:
        print(f"[相似度: {result['similarity']:.2f}] [长度: {result['length']}] {result['content'][:100]}...")
    
    print("\n=== AI上下文 ===")
    ai_context = get_knowledge_for_ai(question)
    print("完整AI上下文:")
    print(ai_context)




