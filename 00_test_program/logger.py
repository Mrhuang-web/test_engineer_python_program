# logger.py
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logger(name, log_file, level=logging.INFO):
    """
    设置日志记录器
    :param name: 日志记录器名称
    :param log_file: 日志文件路径
    :param level: 日志级别
    :return: 配置好的日志记录器
    """
    # 确保日志文件所在目录存在
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 按日期分割日志文件
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(level)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # 创建日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器到记录器
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger