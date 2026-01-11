import logging
import sys
from .config import AppConfig

def setup_logger(name="PolishingApp"):
    """
    配置并返回一个全局日志记录器
    """
    # 确保日志目录存在
    AppConfig.ensure_directories()

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 防止重复添加 Handler
    if logger.handlers:
        return logger

    # 格式化器
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )

    # 1. 控制台 Handler (输出到 PyCharm/终端)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件 Handler (输出到 app.log)
    try:
        file_handler = logging.FileHandler(AppConfig.LOG_FILE, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")

    return logger

# 创建一个默认实例供直接导入
logger = setup_logger()