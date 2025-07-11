import os
# 设置 TensorFlow 日志级别，必须在导入 tensorflow 之前设置
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # 0 = all messages are logged (default); 1 = INFO messages are not printed; 2 = INFO and WARNING messages are not printed; 3 = INFO, WARNING, and ERROR messages are not printed

import tensorflow as tf
# 可以选择性地进一步配置 Python logging
import logging
tf.get_logger().setLevel(logging.ERROR)

from core.MemuInfo import run
import threading

if __name__ == '__main__':

    run()