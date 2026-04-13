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
        self.configparser.read(config_file)
        # 获取mysql
        self.MYSQL_HOST = self.configparser.get('mysql', 'host', fallback="localhost")
        self.MYSQL_PORT = self.configparser.get('mysql', 'port', fallback="3306")
        self.MYSQL_USER = self.configparser.get('mysql', 'user', fallback="root")
        self.MYSQL_PASSWORD = self.configparser.get('mysql', 'password', fallback="123456")
        # 获取redis配置
        self.REDIS_HOST = self.configparser.get('redis', 'host', fallback="localhost")
        self.REDIS_PORT = self.configparser.get('redis', 'port', fallback="6379")
        self.REDIS_DB = self.configparser.get('redis', 'db', fallback="0")
        # 获取日志文件配置
        self.LOG_FILE = self.configparser.get('log', 'log_file', fallback="logs/app.log")


if __name__ == '__main__':
    config = Config()
    print(config.MYSQL_HOST)
    print(config.MYSQL_PORT)
    print(config.MYSQL_USER)
    # print(config.MYSQL_PASSWORD)
    # print(config.REDIS_HOST)
    # print(config.REDIS_PORT)
    # print(config.REDIS_DB)
    ...
