import jieba
from rank_bm25 import BM25L
import logging

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BM25Search():
    def __init__(self, document):
        self.document = document
        self.tokenized_doc = [jieba.lcut(doc) for doc in self.document]
        self.bm25 = BM25L(self.tokenized_doc)
        logger.info("bm25初始化完成")

    def search(self, query):
        tokenizer_query = jieba.lcut(query)
        try:
            score = self.bm25.get_scores(tokenizer_query)
            best_idx = score.argmax()
            best_doc = self.document[best_idx]
            best_score = score[best_idx]
            logger.info(f"检索成功:查询语料：{query}，最佳匹配文档：{best_doc}，最佳得分：{best_score}")
            return best_doc, best_score
        except Exception as e:
            logger.error(f"检索失败：原因为：{e}")


if __name__ == "__main__":
    documents = ["我喜欢编程", "编程很有趣"]
    bm25_model = BM25Search(documents)
    # print(bm25_model)
    query = "他喜欢编程"
    doc, score = bm25_model.search(query)
    print(doc, score)
