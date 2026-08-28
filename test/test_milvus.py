import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sentence_transformers import SentenceTransformer
from src.database.milvus_client import milvus_client
from src.common.logger_setup import edu_rag_logger

model_full_path = os.path.join(project_root, "../models", "bge-small-zh-v1.5")
# 校验路径是否存在
if not os.path.exists(model_full_path):
    raise FileNotFoundError(f"模型目录不存在：{model_full_path}")
edu_rag_logger.info(f"正在加载本地向量模型：{model_full_path}")

# 1. 加载中文嵌入模型，生成文本向量
embed_model = SentenceTransformer(model_full_path, local_files_only=True)

# 读取模型配置里写死的标准维度
model_config_dim = embed_model.get_embedding_dimension()
edu_rag_logger.info(f"【模型配置标注维度】：{model_config_dim}")

# 3. 准备测试知识库文本
test_docs = [
    "Python是一门简洁易用的编程语言，广泛用于AI、后端开发",
    "RAG检索增强生成可以解决大模型知识过时的问题",
    "Milvus是高性能开源向量数据库，专门用于存储Embedding向量"
]

# 生成向量
doc_vectors = embed_model.encode(test_docs).tolist()

# 打印真实运行生成的向量长度
real_vec_dim = len(doc_vectors[0])
print(f"【真实生成向量长度】：{real_vec_dim}")
edu_rag_logger.info(f"【真实生成向量长度】：{real_vec_dim}")

# 对比两个维度是否匹配
if real_vec_dim != model_config_dim:
    edu_rag_logger.warning(
        f"警告！模型标注维度({model_config_dim}) 和实际输出向量维度({real_vec_dim}) 不一致！"
    )

# 2. 自动使用【真实向量维度】创建集合
milvus_client.create_knowledge_collection(dim=real_vec_dim)

# 4. 插入向量库
milvus_client.insert_data(texts=test_docs, vectors=doc_vectors)

# 5. 模拟用户提问，检索相似文本
user_query = "向量数据库有什么作用？"
query_vec = embed_model.encode(user_query).tolist()
search_result = milvus_client.search_similar(query_vector=query_vec, top_k=2)

edu_rag_logger.info(f"用户提问：{user_query}")
edu_rag_logger.info("召回相似知识库内容：")
for hits in search_result:
    for hit in hits:
        edu_rag_logger.info(f"相似度距离：{hit.distance:.4f}  文本：{hit.entity.get('text')}")

milvus_client.close()