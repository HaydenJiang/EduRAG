import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.redis_client import redis_client
from src.common.logger_setup import edu_rag_logger

# 测试读写
TEST_KEY = "edu_rag:test:demo"
redis_client.set(TEST_KEY, "测试Redis缓存数据", expire=300)
val = redis_client.get(TEST_KEY)
edu_rag_logger.info(f"读取缓存key={TEST_KEY}, value={val}")

# 删除测试key
redis_client.delete(TEST_KEY)
edu_rag_logger.info("Redis读写测试完成！")

redis_client.close()