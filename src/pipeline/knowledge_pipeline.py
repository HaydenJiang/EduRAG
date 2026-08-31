import os
import shutil
import tempfile
from typing import Tuple, List
from src.database.minio_client import minio_client
from src.document_parser import parse_file
from src.text_splitter import recursive_splitter
from src.embedding import bge_embedder
from src.database.milvus_client import milvus_client
from src.database.mysql_client import mysql_client
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import PipelineError

class KnowledgePipeline:
    def __init__(self):
        # 临时文件存放目录，自动清理
        self.tmp_dir = tempfile.gettempdir()

    def _download_from_minio(self, bucket: str, obj_key: str, file_md5: str) -> str:
        """从MinIO下载文件到本地临时目录并MD5校验"""
        temp_file_path = os.path.join(self.tmp_dir, os.path.basename(obj_key))
        minio_client.download_file_verify_md5(
            bucket_name=bucket,
            object_key=obj_key,
            save_local_path=temp_file_path,
            expect_md5=file_md5
        )
        edu_rag_logger.info(f"文件下载完成，临时路径：{temp_file_path}")
        return temp_file_path

    def _insert_mysql_meta(
        self,
        kb_id: int,
        origin_name: str,
        bucket: str,
        obj_key: str,
        file_md5: str,
        chunk_count: int
    ) -> int:
        """文档元数据存入MySQL，返回自增文档ID"""
        sql = """
        INSERT INTO knowledge_file (kb_id, origin_filename, bucket, object_key, file_md5, chunk_num, create_time)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """
        mysql_client.execute(sql, args=(kb_id, origin_name, bucket, obj_key, file_md5, chunk_count))
        # 查询刚插入的文档主键id
        res = mysql_client.query("SELECT LAST_INSERT_ID() as file_id;")
        file_id = res["file_id"]
        edu_rag_logger.info(f"文档元数据入库MySQL成功，文档ID：{file_id}")
        return file_id

    def run_pipeline(
        self,
        kb_id: int,
        origin_filename: str,
        bucket: str,
        obj_key: str,
        file_md5: str
    ) -> Tuple[int, int]:
        """
        执行完整知识库入库流水线
        :param kb_id: 知识库ID
        :param origin_filename: 文件原始名称
        :param bucket: minio桶名
        :param obj_key: minio文件路径
        :param file_md5: 文件md5校验值
        :return: (file_id, chunk_count) 文档ID、总分片数量
        """
        temp_file = ""
        try:
            # 1. 下载文件并校验完整性
            temp_file = self._download_from_minio(bucket, obj_key, file_md5)

            # 2. 文档解析提取全文
            full_text = parse_file(temp_file)
            if not full_text.strip():
                raise PipelineError(msg="文档解析后无有效文本，跳过入库")

            # 3. 文本分片
            chunk_list: List[str] = recursive_splitter.RecursiveCharSplitter.split_text(full_text)
            chunk_count = len(chunk_list)
            edu_rag_logger.info(f"文档分片完成，分片总数：{chunk_count}")

            # 4. 批量生成向量
            vector_list = bge_embedder.encode_batch(chunk_list)

            # 5. 向量与文本存入Milvus
            milvus_client.insert_data(texts=chunk_list, vectors=vector_list)

            # 6. 文件元数据写入MySQL
            file_id = self._insert_mysql_meta(
                kb_id=kb_id,
                origin_name=origin_filename,
                bucket=bucket,
                obj_key=obj_key,
                file_md5=file_md5,
                chunk_count=chunk_count
            )

            edu_rag_logger.info(
                f"【流水线全部执行完成】知识库ID:{kb_id} 文档ID:{file_id} 总分片:{chunk_count}"
            )
            return file_id, chunk_count

        except Exception as e:
            edu_rag_logger.error(f"知识库入库流水线失败：{str(e)}")
            raise PipelineError(msg=f"流水线执行异常：{str(e)}") from e
        finally:
            # 清理本地临时文件
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                edu_rag_logger.info(f"临时文件已清理：{temp_file}")


knowledge_pipeline = KnowledgePipeline()