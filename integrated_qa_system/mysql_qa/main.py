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


if __name__ == "__main__":
    qa_system = MysqlQaSystem()
    result = qa_system.query("VMware安装VMware Tools时显示灰色如何解决")
    print(result)
