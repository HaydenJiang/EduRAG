import os
import uuid # 生成唯一文件名，避免同名覆盖
import hashlib # 计算文件MD5，用于完整性校验、秒传
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import Field
from src.common.config_loader import settings
from src.rag_chat.rag_chain import rag_chain
from src.api.schemas import ChatRequest, ChatResponse, UploadResponse
from src.pipeline.knowledge_pipeline import knowledge_pipeline
from src.database.minio_client import minio_client
from src.common.logger_setup import edu_rag_logger

# 知识库存储桶
KB_BUCKET = settings.MINIO.get("bucket", "knowledge-docs")

router = APIRouter(prefix="/rag", tags=["知识库问答"])

@router.post("/chat", response_model=ChatResponse)
async def rag_chat(req: ChatRequest):
    answer = rag_chain.chat(user_query=req.question)
    return ChatResponse(
        code=200,
        msg="请求成功",
        data={"answer": answer}
    )

# 完整多格式文件上传入库接口，对接你现有流水线
@router.post("/upload_doc", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    kb_id: int = Query(default=1, description="知识库ID，默认1")
):
    # 1. 校验文件后缀，复用解析器的格式
    allow_suffix = [".txt", ".md", ".pdf", ".docx", ".ppt", ".pptx"]
    filename = file.filename
    _, suffix = os.path.splitext(filename)
    suffix = suffix.lower()
    if suffix not in allow_suffix:
        return UploadResponse(
            code=400,
            msg=f"不支持该文件格式，仅允许 {allow_suffix}",
            file_key=""
        )

    temp_file = ""
    try:
        # 2. 临时写入本地文件
        unique_name = f"{uuid.uuid4()}_{filename}"
        temp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, unique_name)
        with open(temp_file, "wb") as fw:
            fw.write(await file.read())

        # 3. 计算文件MD5（用于MinIO校验）
        md5_obj = hashlib.md5()
        with open(temp_file, "rb") as fr:
            while chunk := fr.read(8192):
                md5_obj.update(chunk)
        file_md5 = md5_obj.hexdigest()

        # 4. 上传原始文件至MinIO对象存储
        obj_key = f"kb_{kb_id}/{unique_name}"
        minio_client.fput_object(
            bucket_name=KB_BUCKET,
            object_name=obj_key,
            file_path=temp_file
        )
        edu_rag_logger.info(f"文件上传MinIO完成，对象路径：{obj_key} MD5:{file_md5}")

        # 5. 调用流水线：下载MinIO文件→解析→切片→向量化→Milvus入库→MySQL元数据
        file_id, chunk_count = knowledge_pipeline.run_pipeline(
            kb_id=kb_id,
            origin_filename=filename,
            bucket=KB_BUCKET,
            obj_key=obj_key,
            file_md5=file_md5
        )

        return UploadResponse(
            code=200,
            msg=f"文档入库成功，共生成{chunk_count}条知识库片段",
            file_id=file_id,
            chunk_count=chunk_count,
            file_key=obj_key
        )

    except Exception as e:
        edu_rag_logger.error(f"文件上传入库失败：{str(e)}")
        return UploadResponse(
            code=500,
            msg=f"处理异常：{str(e)}",
            file_key=""
        )
    finally:
        # 强制清理本地临时文件
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            edu_rag_logger.info(f"临时文件清理完成：{temp_file}")