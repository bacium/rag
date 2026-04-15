import pymysql
import pandas as pd
import sys
import os

# Add parent directories to path for imports
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from base import Config, logger


# print(f"config: {Config().MYSQL_HOST}")
# logger.info("正在连接mysql数据库...")
class MySQLClient:
    def __init__(self) -> None:
        try:
            self.connection = pymysql.connect(
                host=Config().MYSQL_HOST,
                user=Config().MYSQL_USER,
                port=int(Config().MYSQL_PORT),
                password=Config().MYSQL_PASSWORD,
                database=Config().MYSQL_DATABASE,
            )
            self.cursor = self.connection.cursor()
            logger.info(f"mysql 连接成功")
        except pymysql.MySQLError as e:
            logger.error(f"mysql 连接失败: {e}")
            raise e

    def create_table(self):
        crreate_table_sql = """
        CREATE TABLE IF NOT EXISTS jpkb (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_name VARCHAR(20),
        question VARCHAR(1000),
        answer VARCHAR(1000));
        """
        try:
            self.cursor.execute(crreate_table_sql)
            self.connection.commit()
            logger.info(f"表jpkb创建成功")
        except pymysql.MySQLError as e:
            logger.error(f"表jpkb创建失败: {e}")
            raise e

    def insert_data(self, data_file):
        data = pd.read_csv(data_file)
        try:
            for _, row in data.iterrows():
                insert_data_sql = """INSERT INTO jpkb (subject_name, question,answer) VALUES  (%s,%s,%s)"""
                self.cursor.execute(
                    insert_data_sql, (row["学科名称"], row["问题"], row["答案"])
                )
            self.connection.commit()
            logger.info(f"jpkb插入数据成功")
        except pymysql.MySQLError as e:
            logger.error(f"jpkb插入数据失败: {e}")
            self.connection.rollback()
            raise e

    def query_question(self):
        try:
            self.cursor.execute("SELECT question FROM jpkb")
            questions = self.cursor.fetchall()
            logger.info(f"jpkb查询数据成功")
            return questions
        except pymysql.MySQLError as e:
            logger.error(f"jpkb查询数据失败: {e}")
            return []

    def query_answer(self, question):
        try:
            self.cursor.execute("SELECT answer FROM jpkb WHERE question=%s", question)
            answer = self.cursor.fetchone()
            logger.info(f"jpkb查询为问题{question}成功")
            return answer[0] if answer else None
        except pymysql.MySQLError as e:
            logger.error(f"jpkb查询问题{question}失败: {e}")
            raise e

    def close(self):
        try:
            self.connection.close()
            logger.info(f"mysql 关闭成功")
        except pymysql.MySQLError as e:
            logger.error(f"mysql 断开连接失败: {e}")
            raise e


if __name__ == "__main__":
    mysql_client = MySQLClient()
    # mysql_client.create_table()
    # mysql_client.insert_data("../data/JP学科知识问答.csv")
    # all_questions=mysql_client.query_question()
    # print(f"all_question========>{all_questions}")
    res = mysql_client.query_answer("Tomcat在docker里下载什么版本呢？")
    print(f"res========>{res}")
    # mysql_client.close()
