from pydantic import BaseModel, Field

# 问答请求体
class ChatRequest(BaseModel):
    # 避免超长文本阻塞 LLM
    question: str = Field(min_length=1, max_length=1000, description="用户提问")
    # 限制合理区间，防止恶意传超大值压垮Milvus
    top_k: int = Field(default=5, ge=1, le=20, description="向量召回数量")
    rerank_top: int = Field(default=3, ge=1, le=10, description="重排之后保留条数")

# 问答返回体
class ChatResponse(BaseModel):
    code:int
    msg:str
    data:dict

# 文件上传响应
class UploadResponse(BaseModel):
    code: int
    msg: str
    file_id: int = 0
    chunk_count: int = 0
    file_key: str = ""