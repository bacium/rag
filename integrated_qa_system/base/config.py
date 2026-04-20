import configparser
import os

current_path = os.path.abspath(os.path.abspath(__file__))
# print(f"current_path=======>{current_path}")
base_path = os.path.dirname(current_path)
# print(f"base_path=======>{base_path}")
project_path = os.path.dirname(base_path)
# print(f"project_path=======>{project_path}")

config_file_path = os.path.join(project_path, "config.ini")


class Config(object):
    def __init__(self, config_file=config_file_path):
        self.configparser = configparser.ConfigParser()
        self.configparser.read(filenames=config_file, encoding="utf-8")
        # 获取mysql
        self.MYSQL_HOST = self.configparser.get("mysql", "host", fallback="localhost")
        self.MYSQL_PORT = self.configparser.get("mysql", "port", fallback="3306")
        self.MYSQL_USER = self.configparser.get("mysql", "user", fallback="root")
        self.MYSQL_PASSWORD = self.configparser.get(
            "mysql", "password", fallback="123456"
        )
        self.MYSQL_DATABASE = self.configparser.get(
            "mysql", "database", fallback="subjects_kg"
        )
        # 获取redis配置
        self.REDIS_HOST = self.configparser.get("redis", "host", fallback="localhost")
        self.REDIS_PORT = self.configparser.get("redis", "port", fallback="6379")
        self.REDIS_DB = self.configparser.get("redis", "db", fallback="0")
        self.REDIS_PASSWORD = self.configparser.get(
            "redis", "password", fallback="1234"
        )
        # 获取日志文件配置
        self.LOG_FILE = self.configparser.get(
            "log", "log_file", fallback="logs/app.log"
        )

        # milvus配置
        self.MILVUS_HOST = self.configparser.get("milvus", "host", fallback="localhost")
        self.MILVUS_PORT = self.configparser.get("milvus", "port", fallback="19530")
        self.MILVUS_DATABASE_NAME = self.configparser.get(
            "milvus", "database_name", fallback="bai_test"
        )
        self.MILVUS_COLLECTION_NAME = self.configparser.get(
            "milvus", "collection_name", fallback="edurag_03"
        )

        # 模型配置
        self.MODEL = self.configparser.get("llm", "model", fallback="")
        self.DASHSCOPE_API_KEY = self.configparser.get("llm", "dashscope_api_key")
        self.DASHSCOPE_BASE_URL = self.configparser.get("llm", "dashscope_base_url",
                                                        fallback="https://dashscope.aliyuncs.com/compatible-mode/v1")

        # 检索参数配置
        self.PARENT_CHUNK_SIZE = self.configparser.getint("retrieval", "parent_chunk_size",
                                                          fallback=1200)
        self.CHILD_CHUNK_SIZE = self.configparser.getint("retrieval", "child_chunk_size",
                                                         fallback=300)
        self.CHUNK_OVERLAP = self.configparser.getint("retrieval", "chunk_overlap",
                                                      fallback=50)
        self.RETRIEVAL_K = self.configparser.getint("retrieval", "retrieval_k",
                                                    fallback=3)
        self.CANDIDATE_M = self.configparser.getint("retrieval", "candidate_m",
                                                    fallback=2)


if __name__ == "__main__":
    config = Config()
    # print(config.MYSQL_HOST)
    # print(config.MYSQL_PORT)
    # print(config.MYSQL_USER)
    # print(config.MYSQL_PASSWORD)
    # print(config.REDIS_HOST)
    # print(config.REDIS_PORT)
    # print(config.REDIS_DB)
    # print(config.MILVUS_HOST)
    # print(config.MILVUS_PORT)
    # print(config.DASHSCOPE_BASE_URL)
    # print(config.DASHSCOPE_API_KEY)
    # print(config.MODEL)
    # print(config.PARENT_CHUNK_SIZE)
    # print(config.CHILD_CHUNK_SIZE)
    # print(config.CHUNK_OVERLAP)
    # print(config.RETRIEVAL_K)
    # print(config.CANDIDATE_M)
    # print(config.MILVUS_DATABASE_NAME)
    # print(config.MILVUS_COLLECTION_NAME)
    ...
