import logging
from redis_client import RedisClient

logging.basicConfig(level=logging.INFO, format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s'), )
logger = logging.getLogger(__name__)


def main():
    redis_client = RedisClient()
    key = "test_name"
    value = {"name": "zhangsan", "age": 18}
    # 设置数据
    redis_client.set_data(key, value)
    # 获取数据
    result = redis_client.get_data(key)
    if result:
        logger.info(f"redis get data success====>{result}")
    else:
        logger.error(f"redis get data fail====>失败的key:{key}")
    # 获取redis的回复
    test_query = "query_zhangsan"
    result2 = redis_client.get_answer(test_query)
    if result2:
        logger.info(f"查询缓存成功====>{result2}")
    else:
        logger.error(f"未找到缓存答案====>:{test_query}")
    print(result2)


if __name__ == '__main__':
    main()
