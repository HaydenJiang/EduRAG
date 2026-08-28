import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.mysql_client import mysql_client
from src.common.logger_setup import edu_rag_logger

# 测试查询数据库版本，验证连接正常
res = mysql_client.query("SELECT VERSION() as mysql_version;")
edu_rag_logger.info(f"本地MySQL版本：{res['mysql_version']}")
edu_rag_logger.info("MySQL客户端连通测试通过！")

mysql_client.close()