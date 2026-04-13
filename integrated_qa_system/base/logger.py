import logging
import os
from config import Config

current_path = os.path.abspath(os.path.abspath(__file__))
# print(f"current_path=======>{current_path}")
base_path = os.path.dirname(current_path)
# print(f"base_path=======>{base_path}")
project_path = os.path.dirname(base_path)
# print(f"project_path=======>{project_path}")

log_file_path = os.path.join(project_path, Config().LOG_FILE)


# print("log_file===>", Config().LOG_FILE)


def setup_logginger(log_file=log_file_path):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger("EduRAG")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        # 创建控制台日志输出器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        # 创建文件日志输出器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    return logger


logger = setup_logginger()
