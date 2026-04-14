import jieba

import os, sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from base import logger


def preprocess_text(text):
    try:
        logger.info(f"*********正在处理文本=========> {text}")
        return jieba.lcut(text.lower())
    except Exception as e:
        logger.error(f"*********文本{text}预处理失败！")
        return []


if __name__ == "__main__":
    text = "今天天气不错"
    print(preprocess_text(text))