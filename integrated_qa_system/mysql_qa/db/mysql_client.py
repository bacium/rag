import pymysql
import pandas as pd
import sys
import os

# Add parent directories to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from base import Config, logger

print(f"config: {Config().MYSQL_HOST}")
# logger.info("正在连接mysql数据库...")
class MySQLClient:
    def __init__(self) -> None:
        try:
            self.connection = pymysql.connect(
                host=Config().MYSQL_HOST,
                user=Config().MYSQL_USER,
                password=Config().MYSQL_PASSWORD,
                # database=Config().MYSQL_DATABASE,
            )
            self.cursor = self.connection.cursor()
            logger.info(f"mysql 连接成功")
        except pymysql.MySQLError as e:
            logger.error(f"mysql 连接失败: {e}")
            raise e


if __name__ == "__main__":
    mysql_client = MySQLClient()
