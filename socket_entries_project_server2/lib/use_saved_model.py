import os
import numpy as np
import tensorflow as tf

# 从 weak_password 导入预处理函数和常量
# 确保 weak_password.py 中的这些定义是可导入的
# 如果 preprocess_password 依赖于 weak_password.py 中的其他全局变量，
# 可能需要调整 weak_password.py 或在此处重新定义/导入它们。
try:
    from lib.weak_password import preprocess_password, MAX_LEN, SAVE_PATH
except ImportError as e:
    print(f"Error importing from lib.weak_password: {e}")
    print("Please ensure lib.weak_password.py exists and defines preprocess_password, MAX_LEN, SAVE_PATH.")
    # 提供默认值或退出，取决于应用需求
    MAX_LEN = 32 # 假设的默认值
    SAVE_PATH = '.\\password_strength_model' # 假设的默认值
    def preprocess_password(password):
        print("Warning: Using dummy preprocess_password due to import error.")
        return np.zeros(MAX_LEN) # 返回一个虚拟值

# --- 全局模型变量 --- 
loaded_model = None
model_load_error = None

# --- 模型加载 --- 
def load_model():
    """加载预训练的密码强度模型"""
    global loaded_model, model_load_error
    if loaded_model is not None:
        return # 如果已加载，则不重复加载

    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), SAVE_PATH))
    print(f"Attempting to load model from: {model_path}") # 调试信息

    if os.path.exists(model_path):
        try:
            loaded_model = tf.keras.models.load_model(model_path)
            print(f"模型已成功从 {model_path} 加载。")
            model_load_error = None
        except Exception as e:
            model_load_error = f"加载模型时出错: {e}"
            print(model_load_error)
            loaded_model = None
    else:
        model_load_error = f"错误：模型文件在 {model_path} 未找到。预测功能将不可用。"
        print(model_load_error)
        loaded_model = None

# --- 预测函数 --- 
def predict_password_strength(password):
    """使用加载的模型预测单个密码的强度"""
    global loaded_model, model_load_error

    # 尝试加载模型（如果尚未加载）
    if loaded_model is None and model_load_error is None:
        load_model()

    # 检查模型是否成功加载
    if loaded_model is None:
        return f'模型加载失败: {model_load_error}' if model_load_error else '模型未加载'

    if not password:
        return '无效输入'

    try:
        # 预处理密码
        sequence = preprocess_password(password)
        # 确保输入形状正确 (模型需要批次维度)
        sequence = np.expand_dims(sequence, axis=0)

        # 预测
        proba = loaded_model.predict(sequence, verbose=0)[0]
        predicted_class = np.argmax(proba)

        # 映射到标签
        labels = ['弱', '强', '很强'] # 必须与训练时的类别顺序一致
        return labels[predicted_class]
    except Exception as e:
        return f"预测时发生错误: {e}"

# --- 初始化：尝试加载模型 --- 
# 在模块加载时尝试加载模型，以便后续调用更快
load_model()

# --- (可选) 示例用法 --- 
if __name__ == '__main__':
    print("\n--- use_saved_model.py 测试 ---")
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

    if loaded_model:
        print("使用已加载的模型进行预测：")
        for pwd in test_passwords:
            strength = predict_password_strength(pwd)
            print(f"密码: '{pwd}' -> 强度: {strength}")
    else:
        print("模型未能加载，无法执行预测测试。")
        if model_load_error:
            print(f"错误信息: {model_load_error}")
