print("DEBUG: Loading lib/weak_password.py NOW!") # 添加的调试语句
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, utils
import os

# --- 配置参数 ---
VOCAB_SIZE = 128  # 假设的字符集大小 (ASCII)
MAX_LEN = 32  # 密码最大处理长度
EMBEDDING_DIM = 64
NUM_CLASSES = 3  # 类别：0-弱, 1-强, 2-很强
WEAK_PASSWORD_FILE = '.\\10-million-password-list-top-100000.txt'
SAVE_PATH = '.\\password_strength_model' # 模型保存/加载路径

# --- 全局模型变量 (仅用于训练时) ---
# model = None # 不再需要全局加载的模型变量

# --- 模型加载 (已移动到 use_saved_model.py) ---
# try:
#     if os.path.exists(SAVE_PATH):
#         model = tf.keras.models.load_model(SAVE_PATH)
#         print(f"模型已从 {SAVE_PATH} 加载。")
#     else:
#         print(f"警告：模型文件在 {SAVE_PATH} 未找到。预测功能将不可用，除非先训练并保存模型。")
# except Exception as e:
#     print(f"加载模型时出错: {e}。预测功能将不可用。")

# --- 数据加载与预处理 ---
def load_weak_passwords(filepath):
    """加载弱口令文件"""
    if not os.path.exists(filepath):
        print(f"警告：弱口令文件 {filepath} 不存在。将使用空列表。")
        return set()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = set(line.strip() for line in f if line.strip())
        return passwords
    except Exception as e:
        print(f"加载弱口令文件时出错: {e}")
        return set()





def preprocess_password(password):
    """将密码转换为字符索引序列，并进行填充或截断"""
    # 简单的字符到索引映射 (可以根据需要扩展)
    tokens = [ord(c) for c in password if ord(c) < VOCAB_SIZE]  # 忽略超出范围的字符
    # 填充或截断到 MAX_LEN
    padded_tokens = \
    tf.keras.preprocessing.sequence.pad_sequences([tokens], maxlen=MAX_LEN, padding='post', truncating='post')[0]
    return padded_tokens


# --- 示例数据生成 (根据方案要求，应使用更完善的数据集) ---
def generate_example_data(num_weak=1000, num_strong=50, num_very_strong=50):
    """生成示例数据用于演示，尝试使用更多弱口令并生成一些强/很强密码。"""

    common_passwords = load_weak_passwords(WEAK_PASSWORD_FILE)
    # 弱密码示例 (从加载的列表中随机抽取，或使用默认值)
    if common_passwords:
        num_available_weak = len(common_passwords)
        actual_num_weak = min(num_weak, num_available_weak)
        weak_examples = np.random.choice(list(common_passwords), actual_num_weak, replace=False).tolist()
        print(f"从文件中加载了 {actual_num_weak} 个弱密码示例。")
    else:
        weak_examples = ['123456', 'password', 'qwerty', '111111', 'abcdef']
        print("警告：使用默认的少量弱密码示例。")

    # 强密码示例 (简单生成)
    strong_examples = []
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'  # 包含大小写、数字、符号
    for _ in range(num_strong):
        length = np.random.randint(12, 16)  # 长度 12-15
        strong_examples.append(''.join(np.random.choice(list(chars), length)))

    # 很强密码示例 (简单生成)
    very_strong_examples = []
    for _ in range(num_very_strong):
        length = np.random.randint(16, MAX_LEN + 1)  # 长度 16-MAX_LEN
        very_strong_examples.append(''.join(np.random.choice(list(chars), length)))

    passwords = weak_examples + strong_examples + very_strong_examples
    labels = ([0] * len(weak_examples) +  # 弱
              [1] * len(strong_examples) +  # 强
              [2] * len(very_strong_examples))  # 很强

    # 数据向量化 (对应方案中的密码向量化)
    X = np.array([preprocess_password(p) for p in passwords])
    # 标签 one-hot 编码
    y = utils.to_categorical(labels, num_classes=NUM_CLASSES)

    # 打乱数据
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    X = X[indices]
    y = y[indices]

    return X, y


# --- 模型构建 (CNN + LSTM, 对应方案中的混合模型) ---
def build_model():
    model_instance = models.Sequential()
    model_instance.add(layers.Embedding(input_dim=VOCAB_SIZE, output_dim=EMBEDDING_DIM, input_length=MAX_LEN))  # 字符嵌入层
    model_instance.add(layers.Conv1D(64, 3, activation='relu'))  # CNN层提取局部特征
    model_instance.add(layers.LSTM(128, return_sequences=True))  # LSTM层捕捉时序特征
    model_instance.add(layers.GlobalMaxPooling1D())
    model_instance.add(layers.Dense(64, activation='relu'))
    model_instance.add(layers.Dropout(0.5))
    model_instance.add(layers.Dense(NUM_CLASSES, activation='softmax'))  # 输出层，3分类 (弱/强/很强)

    model_instance.compile(optimizer='adam',
                  loss='categorical_crossentropy',  # 对应方案中的交叉熵损失
                  metrics=['accuracy'])
    return model_instance

# --- 预测函数 (已移动到 use_saved_model.py) ---
# def predict_strength(password):
#     """预测单个密码的强度"""
#     global model # 确保使用全局加载的模型
#     if model is None:
#         return '模型未加载'
#     if not password:
#         return '无效输入'
#     # 预处理
#     sequence = preprocess_password(password)
#     sequence = np.expand_dims(sequence, axis=0)  # 模型需要批次维度
#
#     # 预测
#     proba = model.predict(sequence, verbose=0)[0] # 关闭预测时的冗余输出
#     predicted_class = np.argmax(proba)
#
#     # 映射到标签
#     labels = ['弱', '强', '很强']
#     return labels[predicted_class]


if __name__ == '__main__':
    print("开始训练模型...")
    # 1. 生成数据
    X_train, y_train = generate_example_data(num_weak=5000, num_strong=1000, num_very_strong=1000)
    print(f"生成了 {X_train.shape[0]} 条训练数据。")

    # 2. 构建模型
    training_model = build_model()
    training_model.summary()

    # 3. 训练模型
    print("开始训练...")
    # 可以添加验证集、调整epochs、batch_size等
    history = training_model.fit(X_train, y_train, epochs=10, batch_size=64, validation_split=0.2)
    print("训练完成。")

    # 4. 保存模型
    try:
        training_model.save(SAVE_PATH)
        print(f"模型已保存到 {SAVE_PATH}")
    except Exception as e:
        print(f"保存模型时出错: {e}")

    # --- (可选) 加载刚保存的模型并进行测试 ---
    print("\n加载刚训练的模型进行测试...")
    try:
        loaded_model_for_test = tf.keras.models.load_model(SAVE_PATH)
        print("模型加载成功，开始测试...")

        # 定义一个临时的预测函数用于测试
        def test_predict_strength(password_to_test, model_to_use):
            if not password_to_test:
                return '无效输入'
            sequence = preprocess_password(password_to_test)
            sequence = np.expand_dims(sequence, axis=0)
            proba = model_to_use.predict(sequence, verbose=0)[0]
            predicted_class = np.argmax(proba)
            labels = ['弱', '强', '很强']
            return labels[predicted_class]

        test_passwords = [
            '123456',
            'password123',
            'Qwerty',
            'MyN3wP@ssw0rd!',
            'ThisIsAVeryLongAndSecurePassword123!@#',
            '',
            'Complex$#@&*()_+123',
            'nihao123456',
            'liyekai13735271959',
            'P@ssword123!'
        ]

        for pwd in test_passwords:
            strength = test_predict_strength(pwd, loaded_model_for_test)
            print(f"密码: '{pwd}' -> 强度: {strength}")

    except Exception as e:
        print(f"加载或测试模型时出错: {e}")

