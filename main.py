import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.api.routes import router
from src.database.milvus_client import milvus_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    edu_rag_logger.info("EduRAG-API 全部资源加载完成，服务就绪")
    yield

    milvus_client.close()
    edu_rag_logger.info("EduRAG-API 服务正常关闭，Milvus连接已断开")

app = FastAPI(
    title="Edu-RAG知识库问答后端",
    version="1.0",
    lifespan=lifespan
)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True # 生产部署时改为 reload=False，避免资源重复占用
    )