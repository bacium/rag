"""
Author: 白登超 bacium_dc@163.com
Date: 2026-04-11 17:49:29
LastEditors: 白登超 bacium_dc@163.com
LastEditTime: 2026-04-15 23:21:28
FilePath: \\rag\\integrated_qa_system\\mysql_qa\\retrieval\\bm25_search.py
Description: BM25检索

Copyright (c) 2026 by bacium, All Rights Reserved.
"""

from rank_bm25 import BM25Okapi
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
import numpy as np
from base import logger
from utils.preprocess import preprocess_text
from db.mysql_client import MySQLClient
from cache.redis_client import RedisClient


class BM25Search:
    def __init__(self, mysql_client, redis_client):
        self.mysql_client = mysql_client
        self.redis_client = redis_client
        self.bm25 = None
        self.questions = None
        self.original_questions = None
        self._load_data()

    def _load_data(self):
        self.redis_client.client.delete("qa_original_questions")
        self.redis_client.client.delete("qa_tokenized_questions")
        # 加载数据
        original_key = "qa_original_questions"
        tokenized_key = "qa_tokenized_questions"
        # 先从redis中取原始问题的key
        original_questions = self.redis_client.get_data(original_key)
        tokenized_questions = self.redis_client.get_data(tokenized_key)
        # 判断如果渠道的值为空时从数据库中加载
        if not original_questions or not tokenized_questions:
            self.original_questions = self.mysql_client.query_question()
            print(f"数据库原始数据样本: {self.original_questions[:3]}")  # 加这行
            print(f"q[0] 样本: {self.original_questions[0][0]}, 类型: {type(self.original_questions[0][0])}")
            # 如果数据库中的问题为空时返回None
            if self.original_questions is None:
                logger.warning("数据库中未加载到数据")
                return None
            # 将原始问题分词
            tokenized_questions = [
                preprocess_text(q[0]) for q in self.original_questions
            ]
            # 原始问题和分词数据保存在redis中
            self.redis_client.set_data(
                original_key, [(q[0]) for q in self.original_questions]
            )
            self.redis_client.set_data(tokenized_key, tokenized_questions)
        # 创建BM25模型
        self.questions = tokenized_questions
        self.bm25 = BM25Okapi(self.questions)
        logger.info("BM25模型加载数据成功")

    def _softmax(self, scores):
        exp_scores = np.exp(scores - np.max(scores))
        return exp_scores / exp_scores.sum()

    def search(self, query, threshold=0.85):
        # print(f"query========>{query}")
        if not query or not isinstance(query, str):
            logger.error("无效查询")
            return None, False
        cache_answer = self.redis_client.get_data(query)
        if cache_answer:
            logger.info(f"从缓存中获取答案:{cache_answer}")
            return cache_answer, False
        try:
            tokenize_query = preprocess_text(query)
            scores = self.bm25.get_scores(tokenize_query)
            softmax_scores = self._softmax(scores)
            best_idx = softmax_scores.argmax()
            # print(f"best_idx========>{best_idx}")
            best_score = softmax_scores[best_idx]
            # print(f"best_scores========>{best_score}")
            if best_score >= threshold:
                original_question = self.original_questions[best_idx]
                # print(f"original_question========>{original_question}")
                answer=self.mysql_client.query_answer(original_question)
                # print(f"answer========>{answer}")
                if answer:
                    logger.info(f"从数据库中获取答案:{answer}")
                    self.redis_client.set_data(f"answer:{query}", answer)
                    logger.info(f"查询到答案,{query},softmax相似度:{best_score:.3f}")
                    return answer, False
            logger.info(f"未找到可靠答案，最高 Softmax 相似度: {best_score:.3f}")
            return None, True
        except Exception as e:
            logger.error(f"查询错误:{e}")
            return None, True


if __name__ == "__main__":
    mysql_client = MySQLClient()
    redis_client = RedisClient()
    bm25_search = BM25Search(mysql_client, redis_client)
    bm25_search.search("VMware安装VMware Tools时显示灰色如何解决")
