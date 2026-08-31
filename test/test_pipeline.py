import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.minio_client import minio_client
from src.pipeline import knowledge_pipeline
from src.common.logger_setup import edu_rag_logger

if __name__ == "__main__":
    test_kb_id = 101
    test_file_name = "LLM基础知识.pdf"
    local_test_path = "./tmp_minio_test/" + test_file_name

    obj_key, md5, bucket = minio_client.upload_kb_file(
        kb_id=test_kb_id,
        local_file_path=local_test_path,
        origin_filename=test_file_name,
        operator="test"
    )

    # 执行完整入库流水线
    file_id, chunk_num = knowledge_pipeline.run_pipeline(
        kb_id=test_kb_id,
        origin_filename=test_file_name,
        bucket=bucket,
        obj_key=obj_key,
        file_md5=md5
    )

    edu_rag_logger.info(f"流水线执行成功！文档ID：{file_id}，分片数量：{chunk_num}")