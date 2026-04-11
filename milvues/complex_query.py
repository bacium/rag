from pymilvus import MilvusClient, DataType, AnnSearchRequest, RRFRanker, WeightedRanker
import random


def operate_db():
    # client = MilvusClient(uri="first_milvus.db")
    client = MilvusClient(uri="http://localhost:19530")
    # print(client)
    databases = client.list_databases()
    # print(databases)
    if "milvus_demo" not in databases:
        client.create_database("milvus_demo")
    else:
        client.use_database("milvus_demo")
    return client


client = operate_db()


def complex_query():
    query_film_vector = [
        [0.8896863042430693, 0.370613100114602, 0.23779315077113428, 0.38227915951132996, 0.5997064603128835]]
    dense_search_params = {
        "data": query_film_vector,
        "anns_field": "filmVector",
        "param": {"metric_type": "L2", "nprobe": 10},
        "limit": 2
    }
    request1 = AnnSearchRequest(**dense_search_params)  # 创建一个向量搜索请求，使用ANN近邻算法
    query_poster_vector = [
        [0.02550758562349764, 0.006085637357292062, 0.5325251250159071, 0.7676432650114147, 0.5521074424751443]]
    sparse_search_params = {
        "data": query_poster_vector,
        "anns_field": "posterVector",
        "param": {"metric_type": "COSINE"},
        "limit": 2
    }
    request2 = AnnSearchRequest(**sparse_search_params)
    reqs = [request1, request2]
    # ranker = RRFRanker()
    ranker = WeightedRanker(0.7, 0.3)

    # 执行混合搜索，结合多个向量字段的ANN搜索结果进行排序
    # collection_name: 指定搜索的集合名称为"demo_v3"
    # reqs: 包含多个ANN搜索请求的列表，此处包含filmVector和posterVector两个搜索请求
    # ranker: 使用加权排名器对多路搜索结果进行融合排序，权重分别为0.7和0.3
    # limit: 限制返回的Top-K结果数量为2条
    # output_fields: 指定返回结果中包含的字段
    result = client.hybrid_search(collection_name="demo_v3",
                                  reqs=reqs,
                                  ranker=ranker,
                                  limit=2,
                                  output_fields=["filmVector", "posterVector"],
                                  )
    print(f"result=========>{result}")
    for item in result:
        print("TopK results:")
        for sub_item in item:
            print(sub_item)


def dropout_collection():
    """
    删除名为 'demo_v1' 的集合。
    注意：此操作不可逆，请谨慎使用。
    """
    client.drop_collection("demo_v1")


if __name__ == '__main__':
    # complex_query()
    dropout_collection()
