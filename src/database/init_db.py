import pymysql
from src.common.config_loader import settings

def init_mysql_database():
    mysql_cfg = settings.MYSQL
    # 先不指定数据库连接MySQL服务
    conn = pymysql.connect(
        host=mysql_cfg["host"],
        port=mysql_cfg["port"],
        user=mysql_cfg["user"],
        password=mysql_cfg["password"],
        charset="utf8mb4"
    )
    cursor = conn.cursor()

    # 1. 创建数据库
    sql1 = "CREATE DATABASE IF NOT EXISTS edu_rag_db DEFAULT CHARACTER SET utf8mb4;"
    cursor.execute(sql1)

    # 2. 切换到该数据库
    sql2 = "USE edu_rag_db;"
    cursor.execute(sql2)

    # 3. 创建数据表
    sql3 = """
    CREATE TABLE IF NOT EXISTS knowledge_file (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '文档自增主键',
        kb_id INT NOT NULL COMMENT '所属知识库ID',
        origin_filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
        bucket VARCHAR(128) NOT NULL COMMENT 'MinIO存储桶',
        object_key VARCHAR(512) NOT NULL COMMENT '文件对象路径',
        file_md5 VARCHAR(64) NOT NULL COMMENT '文件MD5校验值',
        chunk_num INT NOT NULL DEFAULT 0 COMMENT '文本分片总数',
        create_time DATETIME NOT NULL DEFAULT NOW() COMMENT '上传时间'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文档元数据表';
    """
    cursor.execute(sql3)

    conn.commit()
    cursor.close()
    conn.close()
    print(" MySQL 数据库 & knowledge_file 数据表初始化完成")

# 创建 knowledge_file 数据表+++++++++++ 后期构建企业级生产环境的数据库 该文件之只执行一次+++++++++++
if __name__ == "__main__":
    init_mysql_database()