import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict


CURRENT_FILE_PATH = Path(__file__)
BASE_DIR = CURRENT_FILE_PATH.parent.parent.parent

# 加载.env环境文件
load_dotenv(dotenv_path=BASE_DIR / ".env")

class GlobalSettings:
    """全局单例配置类，统一读取所有环境变量"""
    # 项目根目录
    PROJECT_ROOT: str = os.getenv("PROJECT_ROOT", str(BASE_DIR))

    # FastAPI服务基础
    SERVER_HOST: str = os.getenv("SERVER_HOST")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL")

    # MySQL本地数据库配置
    MYSQL: Dict = {
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT")),
        "database": os.getenv("MYSQL_DB_NAME"),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD")
    }

    # Redis容器缓存
    REDIS: Dict = {
        "host": os.getenv("REDIS_HOST"),
        "port": int(os.getenv("REDIS_PORT")),
        "db": int(os.getenv("REDIS_DB")),
        "password": os.getenv("REDIS_PASSWORD")
    }

    # Milvus向量库
    MILVUS: Dict = {
        "host": os.getenv("MILVUS_HOST"),
        "port": int(os.getenv("MILVUS_PORT")),
        "collection": os.getenv("MILVUS_COLLECTION")
    }

    # MinIO对象存储
    MINIO: Dict = {
        "endpoint": os.getenv("MINIO_ENDPOINT"),
        "access_key": os.getenv("MINIO_ACCESS_KEY"),
        "secret_key": os.getenv("MINIO_SECRET_KEY")
    }

    # 通义千问大模型
    LLM: Dict = {
        "api_key": os.getenv("DASHSCOPE_API_KEY"),
        "base_url": os.getenv("LLM_BASE_URL"),
        "model_name": os.getenv("LLM_MODEL_NAME")
    }

    # Embedding向量模型路径
    EMBED_MODEL_PATH: str = os.getenv("EMBED_MODEL_PATH")

    # Rerank重排模型路径
    RERANK_MODEL_PATH: str = os.getenv("RERANK_MODEL_PATH")
    RERANK_SCORE_THRESHOLD: float = float(os.getenv("RERANK_SCORE_THRESHOLD", "0.1"))

    # 业务自定义参数
    CUSTOMER_SERVICE_PHONE: str = os.getenv("CUSTOMER_SERVICE_PHONE")

settings = GlobalSettings()