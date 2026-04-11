import redis
import json
from base import Config, logger


class RedisClient(object):
    def __init__(self):
        self.logger = logger
        try:
            self.logger.info('redis init')
            self.client = redis.Redis(
                host=Config().REDIS_HOST,
                port=Config().REDIS_PORT,
                db=Config().REDIS_DB,
                password=Config().REDIS_PASSWORD,
                decode_responses=True
            )
            self.logger.info('redis 连接成功')
        except Exception as e:
            self.logger.error(f'redis 连接失败,异常原因:   {e}')

    def set_data(self, key, value):
        try:
            self.client.set(key, json.dumps(value))
            self.logger.info(f'redis 设置 {key} 成功 ')
        except Exception as e:
            self.logger.error(f'redis 设置 {key} 失败,异常原因:   {e}')

    def get_data(self, key):
        try:
            value = self.client.get(key)
            self.logger.info(f'redis 获取 {key} 成功 ')
            return json.loads(value)
        except Exception as e:
            self.logger.error(f'redis 获取 {key} 失败,异常原因:  {e}')

    def get_answer(self, query):
        try:
            value = self.client.get(query)
            if value:
                self.logger.info(f'从redis 获取 {query}回答成功 ')
                return json.loads(value)
            return None
        except Exception as e:
            self.logger.error(f'redis 获取 {query} 失败,异常原因:{e}')


if __name__ == '__main__':
    redis_client = RedisClient()
    # redis_client.set_data('test', '1234')
    # test_value = redis_client.get_data('test')
    # print(test_value)
    answer = redis_client.get_answer('2+2')
    print(answer)
