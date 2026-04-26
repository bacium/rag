# 导入 BGE-M3 嵌入函数，用于生成文档和查询的向量表示
from milvus_model.hybrid import BGEM3EmbeddingFunction
# 导入 Milvus 相关类，用于操作向量数据库
from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker
# 导入 Document 类，用于创建文档对象
from langchain.docstore.document import Document
# 导入 CrossEncoder，用于重排序和 NLI 判断
from sentence_transformers import CrossEncoder
# 导入 hashlib 模块，用于生成唯一 ID 的哈希值
import hashlib
import torch
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
        self.reranker = CrossEncoder(model_name_or_path="../models/bge-reranker-large")
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


if __name__ == "__main__":
    vectorStore = VectorStore()
