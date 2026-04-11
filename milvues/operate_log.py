import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='logInfo.log',
                    filemode="a"
                    )


def set_operate_log(log_file):
    logger = logging.getLogger(log_file)
    logger.debug("debugger_test")
    logger.info("info_test")
    logger.warning("warning_test")
    logger.error("error_test")
    logger.critical("critical_test")


# 设置文件和控制台输出
def set_logger_type():
    logger = logging.getLogger('logger_type')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(filename='logInfo.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.debug("debugger_test")
    logger.info("info_test")
    logger.warning("warning_test")
    logger.error("error_test")
    logger.critical("critical_test")


if __name__ == '__main__':
    # set_operate_log('test')
    set_logger_type()
