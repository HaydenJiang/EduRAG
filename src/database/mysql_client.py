import pymysql
from pymysql.cursors import DictCursor
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import DatabaseConnectError

class MysqlClient:
    _instance = None    # 存唯一实例，实现单例复用。全局永远只创建 1 个 MysqlClient 对象，只建立 1 条数据库连接
    _pool = None        # 预留连接池变量(后续优化)

    def __new__(cls):   # 先分配内存、生成空白对象
        if cls._instance is None:
            cls._instance = super().__new__(cls)    # 第一次创建：生成空白对象
            cls._instance._init_conn()              # 调用内部初始化方法，建立MySQL连接
        return cls._instance                        # 第二次、第三次创建，直接返回已经存在的实例

    def _init_conn(self):
        """初始化数据库连接"""
        mysql_cfg = settings.MYSQL
        try:
            self.conn = pymysql.connect(
                host=mysql_cfg["host"],
                port=mysql_cfg["port"],
                user=mysql_cfg["user"],
                password=mysql_cfg["password"],
                database=mysql_cfg["database"],
                charset="utf8mb4",
                cursorclass=DictCursor,
                autocommit=True # 单条操作自动落库
            )
            self.cursor = self.conn.cursor()
            edu_rag_logger.info(f"MySQL[{mysql_cfg['database']}] 连接成功")
        except Exception as e:
            edu_rag_logger.error(f"MySQL连接失败：{str(e)}")
            raise DatabaseConnectError(db_name="MySQL") from e

    def query(self, sql: str, args=None):
        """查询单条数据"""
        args = args or ()
        self.cursor.execute(sql, args)
        return self.cursor.fetchone()

    def query_list(self, sql: str, args=None):
        """查询多条数据"""
        args = args or ()
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def execute(self, sql: str, args=None):
        """增/删/改操作"""
        args = args or ()
        self.cursor.execute(sql, args)
        return self.cursor.rowcount

    def close(self):
        """关闭连接"""
        if self.conn:
            self.cursor.close()
            self.conn.close()
            edu_rag_logger.info("MySQL 连接已关闭")


mysql_client = MysqlClient()