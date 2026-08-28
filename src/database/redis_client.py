import redis
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import DatabaseConnectError

class RedisClient:
    _instance = None
    client: redis.Redis

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        redis_cfg = settings.REDIS
        try:
            self.client = redis.Redis(
                host=redis_cfg["host"],
                port=redis_cfg["port"],
                db=redis_cfg["db"],
                password=redis_cfg["password"],
                decode_responses=True,  # 自动把bytes转为字符串，不用手动解码
                socket_timeout=5
            )
            # 连通性测试
            self.client.ping()
            edu_rag_logger.info(f"Redis db{redis_cfg['db']} 连接成功")
        except Exception as e:
            edu_rag_logger.error(f"Redis连接失败: {str(e)}")
            raise DatabaseConnectError(db_name="Redis") from e

    def set(self, key: str, value, expire: int = None):
        """写入缓存，expire单位：秒"""
        return self.client.set(key, value, ex=expire)

    def get(self, key: str):
        """读取缓存"""
        return self.client.get(key)

    def delete(self, key: str):
        """删除key"""
        return self.client.delete(key)

    def close(self):
        self.client.close()
        edu_rag_logger.info("Redis 连接已关闭")


redis_client = RedisClient()