import time
from cache.redis_client import RedisClient
from utils.preprocess import preprocess_text
from db.mysql_client import MySQLClient
from base import logger
from retrieval.bm25_search import BM25Search


class MysqlQaSystem:
    def __init__(self):
        self.mysql_client = MySQLClient()
        self.redis_client = RedisClient()
        self.bm25_search = BM25Search(self.mysql_client, self.redis_client)
        self.logger = logger

    def query(self, query):
        start_time = time.time()
        self.logger.info(f"用户查询: {query}")
        answer, _ = self.bm25_search.search(query, threshold=0.85)
        if answer:
            self.logger.info(f"查询到答案: {answer}")
        else:
            self.logger.info("未找到答案")
            answer = "Mysql中未查询到结果"
        process_time = time.time() - start_time
        self.logger.info(f"处理时间: {process_time:.3f}秒")
        return answer

def main():
    mysql_qa=MysqlQaSystem()
    logger.info("mysql问答系统启动成功")
    print("欢迎使用mysql问答系统")
    print("输入查询进行问答，输入 'exit' 退出。")
    try:
        while True:
            prompt_message = input("\n请输入查询: ")
            if prompt_message.lower() == "exit":
                print("退出成功!")
                logger.info("mysql问答系统已退出")
                break
            else:
                logger.info(f"用户查询: {prompt_message}")
                answer = mysql_qa.query(prompt_message)
                logger.info(f"查询结果: {answer}")
    except Exception as e:
        logger.error(f"处理用户查询时发生错误: {e}")





if __name__ == "__main__":

    main()
