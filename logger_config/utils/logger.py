import logging
import os

logging.basicConfig(level=logging.DEBUG)
base_path = os.path.abspath(__file__)
# print(f"base_path=======>{base_path}")
parent_path = os.path.dirname(base_path)
# print(f"parent_path=======>{parent_path}")
target_path = os.path.dirname(parent_path)
# print(f"target_path=======>{target_path}")
log_file = os.path.join(target_path, 'logs/logInfo.log')


def setup_logger(name, log_file=log_file):
    logger = logging.getLogger(name)
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler(filename=log_file, encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger


if __name__ == '__main__':
    setup_logger('test')
