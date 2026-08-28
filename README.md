# 集成式问答系统（RAG+结构化SQL问答）
企业级分层架构，支持知识库向量检索问答

## 技术栈

### 1. Web 服务层
- FastAPI：高性能异步 Web 框架，提供文件上传、问答 HTTP 接口
- uvicorn：ASGI 服务运行器
- Pydantic：请求 / 响应参数校验、数据模型封装

### 2. RAG 核心链路
大模型服务
- 通义千问 Qwen3.7-plus，基于 Dashscope OpenAI 兼容接口调用

向量 & 重排模型（本地离线部署）
- Embedding：bge-small-zh-v1.5（512 维中文向量）
- Rerank 重排：bge-reranker-v2-m3（CrossEncoder 精细化相关性排序）

向量数据库
- Milvus 2.4.4：高性能向量检索引擎，存储文档切片向量

### 3. 数据存储中间件（Docker 一键部署）

1. MySQL：存储知识库、上传文档元数据表
2. Redis：向量结果缓存、会话缓存、任务队列支撑
3. MinIO：对象存储，持久化用户上传原始 PDF/Word/PPT 等文件
4. Etcd：Milvus 依赖元数据存储组件

### 4. 文档解析模块（多格式文件提取文本）

- TXT/Markdown：chardet 自动编码识别
- PDF：PyPDF2
- Word(docx)：python-docx
- PPT/PPTX：python-pptx

## 项目结构

```
EduRAG/
├── .env                          # 全局环境配置（中间件、模型、LLM密钥）
├── docker-compose.yml            # Milvus/MinIO/Redis/Etcd 容器编排
├── main.py                       # FastAPI 服务入口，生命周期管理
├── tmp/                          # 上传临时文件目录（运行自动生成）
├── logs/                         # 日志存储目录（运行自动生成）
├── models/                       # 本地大模型存放目录
│   ├── bge-small-zh-v1.5/        # 向量Embedding模型
│   └── bge-reranker-v2-m3/       # 重排CrossEncoder模型
├── volumes/                      # Docker持久化数据挂载目录
└── src/
    ├── api/                      # 接口层
    │   ├── routes.py             # /rag/upload_doc /rag/chat 路由逻辑
    │   └── schemas.py            # Pydantic 请求/响应模型
    ├── common/                   # 全局通用基础组件
    │   ├── config_loader.py      # 配置单例settings
    │   ├── exceptions.py         # 统一业务异常类
    │   ├── logger_setup.py       # 全局日志初始化
    │   └── utils.py              # 文本/时间/文件工具函数
    ├── database/                 # 所有中间件客户端
    │   ├── init_db.py            # MySQL建库建表初始化脚本
    │   ├── milvus_client.py      # Milvus向量库单例客户端
    │   ├── minio_client.py       # MinIO对象存储客户端
    │   ├── mysql_client.py       # MySQL关系库客户端
    │   └── redis_client.py       # Redis缓存客户端
    ├── document_parser/          # 多格式文档解析模块
    │   ├── base_parser.py        # 解析器抽象基类
    │   ├── docx_parser.py        # Word解析器
    │   ├── pdf_parser.py         # PDF纯文本解析器
    │   ├── ppt_parser.py         # PPT/PPTX解析器
    │   ├── txt_parser.py         # TXT/Markdown解析器
    │   └── parser_factory.py     # 解析器工厂，统一对外parse_file
    ├── text_splitter/            # 文本分片模块
    │   ├── base_splitter.py      # 分片器抽象基类
    │   └── recursive_splitter.py # 递归中文分片实现（全局默认分片器）
    ├── embedding/                # 向量编码模块
    │   ├── base_embedder.py      # 向量器抽象基类
    │   └── bge_embedder.py       # BGE本地向量化实现（Redis缓存+批量推理）
    ├── retrieval/                # 检索重排模块
    │   └── reranker.py           # BGE CrossEncoder重排工具
    ├── pipeline/                 # 文档入库一站式流水线
    │   └── knowledge_pipeline.py # 完整上传入库链路封装
    └── rag_chat/                 # RAG问答主链路
        ├── llm_client.py          # 阿里云通义千问兼容客户端
        ├── prompt_template.py     # 问答提示词模板管理
        └── rag_chain.py           # 完整RAG问答串联逻辑（检索+重排+LLM）
```

## 启动步骤

```
# 编辑环境，配置DASHSCOPE_API_KEY

# 克隆项目后，进入项目根目录
cd EduRAG

# 后台启动所有依赖中间件
docker-compose up -d
# 查看容器运行状态
docker-compose ps

# 安装依赖
pip install -r requirements.txt

# 初始化 MySQL 数据库与数据表
python src/database/init_db.py
```

```
# 启动应用
python main.py
```
