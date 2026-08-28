import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import os
from src.database.minio_client import minio_client
from src.common.logger_setup import edu_rag_logger
from src.common.utils import safe_mkdir

# ========== 测试参数 ==========
TEST_KB_ID = 101
TEST_ORIGIN_NAME = "RAG.md"
TEST_OPERATOR = "test_admin"
tmp_dir = "../tmp_minio_test"
safe_mkdir(tmp_dir)

# 1. 生成测试文件
test_file_path = os.path.join(tmp_dir, TEST_ORIGIN_NAME)
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write("EduRAG教育知识库：文档上传、向量解析、问答检索完整流程")

# 2. 上传文件（自动校验大小、后缀、生成UUID路径、计算MD5）
obj_key, file_md5, bucket = minio_client.upload_kb_file(
    kb_id=TEST_KB_ID,
    local_file_path=test_file_path,
    origin_filename=TEST_ORIGIN_NAME,
    operator=TEST_OPERATOR
)
edu_rag_logger.info(f"上传结果：桶={bucket} | 存储路径={obj_key} | MD5={file_md5}")

# 3. 下载文件 + MD5完整性校验
download_path = os.path.join(tmp_dir, "下载校验文件.md")
minio_client.download_file_verify_md5(bucket, obj_key, download_path, expect_md5=file_md5)

# 4. 健康检查
health_status = minio_client.health_check()
edu_rag_logger.info(f"MinIO健康状态：{health_status}")

# 5. 删除云端文件
minio_client.delete_file(bucket, obj_key, operator=TEST_OPERATOR)
edu_rag_logger.info("===== MinIO企业级全功能测试全部完成 =====")

minio_client.close()