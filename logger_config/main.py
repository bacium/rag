from utils.logger import setup_logger

logger = setup_logger("MainApp")


def process_data(data):
    logger.info("开始处理数据")
    if not data:
        logger.warning("数据为空")
        return None
    data.upper()
    print(data.upper())
    logger.info("处理数据完成")


def main(data):
    logger.info("程序启动")
    if not data:
        logger.warning("数据为空")
    process_data(data)
    logger.info("程序结束")


if __name__ == '__main__':
    main("test,hello")