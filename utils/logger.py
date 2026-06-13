import logging
import os
from config.settings import BASE_DIR

# 拼接日志文件夹路径
LOG_DIR = os.path.join(BASE_DIR, "logs")
# 不存在则自动创建日志目录
os.makedirs(LOG_DIR, exist_ok=True)

# 定义日志打印格式：时间-模块名-日志级别-日志内容
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# 全局日志基础配置
logging.basicConfig(
    level=logging.INFO,
    # 套用自定义格式
    handlers=[
        # 日志写入本地文件，utf-8避免中文乱码
        logging.FileHandler(os.path.join(LOG_DIR, "logs.log"), encoding="utf-8"),
        # 同时控制台打印日志
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志实例，实现模块分级日志
    :param name:当前模块名
    :return:日志对象
    """
    return logging.getLogger(name)