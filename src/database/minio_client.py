import os
import uuid
import hashlib
from typing import Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from minio import Minio
from minio.error import S3Error
from pydantic import BaseModel, Field
from urllib3 import PoolManager
from minio.error import S3Error

from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import (
    DatabaseConnectError,
    FileTooLargeError,
    FileSuffixNotAllowedError,
    FileNotExistError,
    FileMd5MismatchError
)

# ===================== 业务常量配置 =====================
# 允许上传后缀
ALLOW_SUFFIX = {".pdf", ".docx", ".ppt", ".txt", ".md"}
# 最大单文件 500MB
MAX_FILE_SIZE = 500 * 1024 * 1024
# 上传下载重试3次，间隔2秒
RETRY_TIMES = 3
RETRY_WAIT_SEC = 2
# 分片上传单片大小 10MB
PART_SIZE = 10 * 1024 * 1024

# 多桶配置模型
class BucketConfig(BaseModel):
    docs_bucket: str = Field(default="edu-knowledge-docs", description="教学文档桶")
    image_bucket: str = Field(default="edu-knowledge-img", description="图片素材桶")
    temp_bucket: str = Field(default="edu-temp-cache", description="临时缓存桶")

# ===================== MinIO客户端主类 =====================
class MinioClient:
    _instance: Optional["MinioClient"] = None
    bucket_cfg: BucketConfig
    client: Minio

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """初始化：超时配置 + 多桶创建 + 连通校验"""
        minio_cfg = settings.MINIO
        self.bucket_cfg = BucketConfig()
        try:
            # 通过 urllib3 PoolManager 设置连接/读取超时
            http_client = PoolManager(
                timeout=15,  # 全局超时15秒
                retries=3
            )
            self.client = Minio(
                endpoint=minio_cfg["endpoint"],
                access_key=minio_cfg["access_key"],
                secret_key=minio_cfg["secret_key"],
                secure=False,
                http_client=http_client
            )
            # 批量创建所有业务桶
            all_buckets = [
                self.bucket_cfg.docs_bucket,
                self.bucket_cfg.image_bucket,
                self.bucket_cfg.temp_bucket
            ]
            for bucket in all_buckets:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    edu_rag_logger.info(f"MinIO 存储桶 [{bucket}] 创建完成")
            edu_rag_logger.info("MinIO 对象存储初始化连接成功")
        except S3Error as e:
            edu_rag_logger.error(f"MinIO初始化连接失败: {str(e)}")
            raise DatabaseConnectError(db_name="MinIO对象存储") from e

    def _calc_file_md5(self, file_path: str) -> str:
        """计算文件MD5哈希，用于完整性校验"""
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def _check_file_valid(self, local_file_path: str):
        """上传前置校验：大小、后缀"""
        if not os.path.isfile(local_file_path):
            raise FileNotFoundError("待上传文件不存在")
        # 校验文件大小
        file_size = os.path.getsize(local_file_path)
        if file_size > MAX_FILE_SIZE:
            raise FileTooLargeError(max_size=500)
        # 校验后缀
        _, suffix = os.path.splitext(local_file_path)
        suffix = suffix.lower()
        if suffix not in ALLOW_SUFFIX:
            raise FileSuffixNotAllowedError(allow_suffix="pdf,docx,ppt,txt,md")

    def gen_object_key(self, kb_id: int, origin_filename: str) -> str:
        """文件隔离：知识库ID+UUID 前缀，防止文件名覆盖
        格式：knowledge_{kb_id}/{uuid4()}-原文件名
        """
        file_uuid = str(uuid.uuid4())
        return f"knowledge_{kb_id}/{file_uuid}-{origin_filename}"

    @retry(
        stop=stop_after_attempt(RETRY_TIMES),
        wait=wait_fixed(RETRY_WAIT_SEC),
        retry=retry_if_exception_type((S3Error, ConnectionError)),
        before_sleep=lambda s: edu_rag_logger.warning(f"上传失败，正在第{s.attempt_number}次重试")
    )
    def upload_kb_file(
        self,
        kb_id: int,
        local_file_path: str,
        origin_filename: str,
        operator: str = "admin"
    ) -> Tuple[str, str, str]:
        """
        分片流式上传教学文档
        :param kb_id: 知识库ID
        :param local_file_path: 本地文件路径
        :param origin_filename: 原始文件名
        :param operator: 操作人
        :return: object_key, file_md5, file_bucket
        """
        # 1.前置校验
        self._check_file_valid(local_file_path)
        # 2.生成唯一存储路径
        obj_key = self.gen_object_key(kb_id, origin_filename)
        target_bucket = self.bucket_cfg.docs_bucket
        # 3.计算MD5
        file_md5 = self._calc_file_md5(local_file_path)
        file_size = os.path.getsize(local_file_path)

        # 4.分片流式上传
        self.client.fput_object(
            bucket_name=target_bucket,
            object_name=obj_key,
            file_path=local_file_path,
            part_size=PART_SIZE
        )
        # 操作日志埋点
        edu_rag_logger.info(
            f"文件上传完成 | 操作人:{operator} | 知识库ID:{kb_id} | "
            f"存储路径:{obj_key} | 文件大小:{file_size} | MD5:{file_md5}"
        )
        return obj_key, file_md5, target_bucket

    @retry(
        stop=stop_after_attempt(RETRY_TIMES),
        wait=wait_fixed(RETRY_WAIT_SEC),
        retry=retry_if_exception_type((S3Error, ConnectionError)),
        before_sleep=lambda s: edu_rag_logger.warning(f"下载失败，正在第{s.attempt_number}次重试")
    )
    def download_file_verify_md5(
        self,
        bucket_name: str,
        object_key: str,
        save_local_path: str,
        expect_md5: str
    ):
        """下载文件 + MD5校验防篡改"""
        try:
            self.client.fget_object(
                bucket_name=bucket_name,
                object_name=object_key,
                file_path=save_local_path
            )
        except S3Error as e:
            if "NoSuchKey" in str(e):
                raise FileNotExistError()
            raise

        # 校验MD5
        real_md5 = self._calc_file_md5(save_local_path)
        if real_md5 != expect_md5:
            os.remove(save_local_path)
            raise FileMd5MismatchError()
        edu_rag_logger.info(f"文件下载+MD5校验通过 | 存储路径:{object_key}")

    def delete_file(self, bucket_name: str, object_key: str, operator: str = "admin"):
        """删除文件，操作日志留存"""
        try:
            self.client.remove_object(bucket_name, object_key)
            edu_rag_logger.info(
                f"文件删除成功 | 操作人:{operator} | 存储路径:{object_key}"
            )
        except S3Error as e:
            if "NoSuchKey" in str(e):
                raise FileNotExistError()
            raise

    def health_check(self) -> bool:
        """健康检查接口"""
        try:
            self.client.list_buckets()
            return True
        except Exception as e:
            edu_rag_logger.error(f"MinIO健康检测异常: {str(e)}")
            return False

    def close(self):
        """资源释放"""
        edu_rag_logger.info("MinIO客户端资源释放完成")


minio_client = MinioClient()