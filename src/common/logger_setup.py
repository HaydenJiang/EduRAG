import logging
from logging import handlers
import os
from src.common.config_loader import settings

# 读取日志配置
LOG_LEVEL = settings.LOG_LEVEL
LOG_FOLDER = "./logs"
LOG_FILE_PATH = os.path.join(LOG_FOLDER, "edu_rag_app.log")

# 自动创建logs文件夹
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# 日志输出格式化模板
LOG_FORMAT = logging.Formatter(
    fmt="%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 全局日志对象
edu_rag_logger = logging.getLogger("EduRagSystem")
edu_rag_logger.setLevel(LOG_LEVEL)
edu_rag_logger.propagate = False # 关闭日志向上传递

# 1. 控制台打印日志
console_handler = logging.StreamHandler() # 创建控制台输出处理器
console_handler.setFormatter(LOG_FORMAT)
edu_rag_logger.addHandler(console_handler)

# 2. 文件滚动日志：单个文件最大10MB，最多保存5个备份
file_handler = handlers.TimedRotatingFileHandler(
    filename=LOG_FILE_PATH,
    when="D",
    interval=1,
    backupCount=30,
    encoding="utf-8"
)
file_handler.setFormatter(LOG_FORMAT)
edu_rag_logger.addHandler(file_handler)