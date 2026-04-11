import logging

logging.basicConfig(level=logging.INFO,
                    format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                    )

logger = logging.getLogger(__name__)


class Config():
    def __init__(self):
        self.REDIS_HOST = '127.0.0.1'
        self.REDIS_PORT = 6379
        self.REDIS_DB = 0
        self.REDIS_PASSWORD = '1234'


if __name__ == '__main__':
    config = Config()
    logger.info(config.__dict__)
