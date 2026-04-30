# 导入 BGE-M3 嵌入函数，用于生成文档和查询的向量表示
from milvus_model.hybrid import BGEM3EmbeddingFunction
# 导入 Milvus 相关类，用于操作向量数据库
from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker
# 导入 Document 类，用于创建文档对象
from langchain_core.documents import Document
# 导入 CrossEncoder，用于重排序和 NLI 判断
from sentence_transformers import CrossEncoder
# 导入 hashlib 模块，用于生成唯一 ID 的哈希值
from document_processor import *
import hashlib
import torch
import numpy as np
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from base import logger, Config

conf = Config()


class VectorStore:
    def __init__(self, collection_name=conf.MILVUS_COLLECTION_NAME,
                 host=conf.MILVUS_HOST,
                 port=conf.MILVUS_PORT,
                 database=conf.MILVUS_DATABASE_NAME):
        self.milvus_client = MilvusClient(host=host, port=port, db_name=database)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.host = host
        self.port = port
        self.database = database
        self.collection_name = collection_name
        self.logger = logger
        # self.reranker = CrossEncoder(model_name_or_path="../models/bge-reranker-large")
        self.reranker = CrossEncoder(
            model_name_or_path="../models/bge-reranker-large",
            automodel_args={"ignore_mismatched_sizes": True},
            tokenizer_args={"use_fast": False}
        )
        self.embedding_function = BGEM3EmbeddingFunction(model_name="../models/bge-m3",

                                                         use_fp16=(self.device == "cuda"), device=self.device)
        self.dense_dim = self.embedding_function.dim["dense"]
        self._create_or_load_collection()

    def _create_or_load_collection(self):
        if self.collection_name not in self.milvus_client.list_collections():
            self.logger.info(f"集合{self.collection_name}不存在，创建中...")
            # 创建集合 Schema，禁用自动 ID，启用动态字段
            schema = self.milvus_client.create_schema(auto_id=False, enable_dynamic_field=True)
            # 添加 ID 字段，作为主键，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, max_length=100)
            # 添加文本字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            # 添加稠密向量字段，FLOAT_VECTOR 类型，维度由嵌入函数指定
            schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=self.dense_dim)
            # 添加稀疏向量字段，SPARSE_FLOAT_VECTOR 类型
            schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
            # 添加父块 ID 字段，VARCHAR 类型，最大长度 100
            schema.add_field(field_name="parent_id", datatype=DataType.VARCHAR, max_length=100)
            # 添加父块内容字段，VARCHAR 类型，最大长度 65535
            schema.add_field(field_name="parent_content", datatype=DataType.VARCHAR, max_length=65535)
            # 添加学科类别字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=50)
            # 添加时间戳字段，VARCHAR 类型，最大长度 50
            schema.add_field(field_name="timestamp", datatype=DataType.VARCHAR, max_length=50)
            # 创建索引参数对象
            index_params = self.milvus_client.prepare_index_params()
            # 为稠密向量字段添加 IVF_FLAT 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="dense_vector",
                index_name="dense_index",
                index_type="IVF_FLAT",
                metric_type="IP",
                params={"nlist": 128}
            )
            # 为稀疏向量字段添加 SPARSE_INVERTED_INDEX 索引，度量类型为内积 (IP)
            index_params.add_index(
                field_name="sparse_vector",
                index_name="sparse_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="IP",
                params={"drop_ratio_build": 0.2}
            )

            # 创建 Milvus 集合，应用定义的 Schema 和索引参数
            self.milvus_client.create_collection(collection_name=self.collection_name, schema=schema,
                                                 index_params=index_params)
            self.logger.info(f"已创建集合{self.collection_name}")
        else:
            self.logger.info(f"已连接集合{self.collection_name}，正在加载到内存中")
            self.milvus_client.load_collection(self.collection_name)

    def add_documents(self, documents):
        texts = [doc.page_content for doc in documents]
        # print(f"texts======>{ texts}")
        # 文本进行向量化处理
        embeddings = self.embedding_function(texts)
        # print(f"embeddings========>{embeddings}")
        data = []
        for i, doc in enumerate(documents):
            doc_id = hashlib.md5(doc.page_content.encode("utf-8")).hexdigest()
            sparse_vector = {}
            row = embeddings["sparse"][i]
            row_csr = row.tocsr()  # coo_array -> csr_array
            sparse_vector = {int(index): float(value) for index, value in zip(row_csr.indices, row_csr.data)}
            # Milvus FLOAT_VECTOR 强制要求 np.float32 类型
            dense_vector = np.array(embeddings["dense"][i], dtype=np.float32).tolist()
            data.append({
                "id": doc_id,
                "text": doc.page_content,
                "dense_vector": dense_vector,
                "sparse_vector": sparse_vector,
                "parent_id": doc.metadata["parent_chunk_id"],
                "parent_content": doc.metadata["parent_chunk_content"],
                "source": doc.metadata.get("source", "unknown"),
                "timestamp": doc.metadata.get("timestamp", "unknown")
            })
        if data:
            try:
                self.milvus_client.upsert(collection_name=self.collection_name, data=data)
                self.logger.info(f"成功向集合 {self.collection_name} 添加 {len(data)} 个文档")
            except Exception as e:
                self.logger.error(f"Milvus Upsert 失败: {e}")
                raise e

    def hybrid_search_with_rerank(self, query, k=conf.RETRIEVAL_K, source_filter="ai"):
        query_embedding = self.embedding_function([query])
        self.logger.info(f"对查询 {query} 进行混合搜索{query_embedding}")
        # 稠密查询向量
        dense_query_vector = query_embedding["dense"][0]
        # 稀疏查询向量
        sparse_query_row = query_embedding["sparse"][0]
        query_row = sparse_query_row.tocsr()
        sparse_query_vector = {int(index): float(value) for index, value in zip(query_row.indices, query_row.data)}
        # Milvus FLOAT_VECTOR 强制要求 np.float32 类型
        dense_vector = np.array(dense_query_vector, dtype=np.float32).tolist() \
            # 初始化过滤表达式，默认不过滤
        filter_expr = f"source == '{source_filter}'" if source_filter else ""
        # 稠密向量请求
        dense_request = AnnSearchRequest(
            data=[dense_vector],
            anns_field="dense_vector",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=k,
            expr=filter_expr
        )
        # 稀疏向量请求
        sparse_request = AnnSearchRequest(
            data=[sparse_query_vector],
            anns_field="sparse_vector",
            param={"metric_type": "IP", "params": {}},
            limit=k,
            expr=filter_expr
        )
        reranker = WeightedRanker(1.0, 0.7)
        reranker_request = self.milvus_client.hybrid_search(collection_name=self.collection_name,
                                                            reqs=[dense_request, sparse_request],
                                                            ranker=reranker,
                                                            rerank_param={"metric_type": "IP", "params": {}},
                                                            output_fields=["text", "parent_id", "parent_content",
                                                                           "source", "timestamp"])
        print(f"reranker_request==========>{reranker_request}")


if __name__ == "__main__":
    vectorStore = VectorStore()
    # dir_path = "/Users/baidengchao/Desktop/project/Rag_code/integrated_qa_system/rag_qa/data/ai_data"
    # dir_path = "C:\\Users\\bai\\Desktop\\project\\rag\\integrated_qa_system\\rag_qa\\data\\ai_data"
    # chunk_result = process_document(dir_path)
    # vectorStore.add_documents(chunk_result)
    vectorStore.hybrid_search_with_rerank("什么是大模型")
