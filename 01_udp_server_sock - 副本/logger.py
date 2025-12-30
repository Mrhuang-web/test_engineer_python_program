import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

def setup_logger(name, log_file, level=logging.INFO, log_format=None):
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 文件日志
    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8")
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(level)

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    formatter = logging.Formatter(log_format or '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(console_handler)
    return logger