import os
import hashlib
from typing import List
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sentence_transformers import SentenceTransformer
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import LLMRequestError
from src.database.redis_client import redis_client
from src.embedding.base_embedder import BaseEmbedder

# 常量配置
EMBED_CACHE_PREFIX = "embed_cache:" # Redis缓存key前缀，区分项目内不同缓存数据
EMBED_CACHE_EXPIRE = 86400          # 缓存1天
RETRY_TIMES = 2                     # 向量化失败最多重试2次
RETRY_WAIT = 1                      # 每次重试前等待1秒

class BgeLocalEmbedder(BaseEmbedder):
    """BGE 向量模型具体落地实现（缓存、重试、批量、离线加载全逻辑）"""
    def __init__(self):
        self._load_model()

    def _load_model(self):
        # 拼接本地模型绝对路径
        model_path = os.path.join(settings.PROJECT_ROOT, "models", "bge-small-zh-v1.5")
        edu_rag_logger.info(f"加载本地向量模型：{model_path}")
        try:
            self.model = SentenceTransformer(model_path, local_files_only=True)
        except Exception as e:
            edu_rag_logger.error(f"向量模型加载失败：{str(e)}")
            raise LLMRequestError(msg="本地BGE模型加载异常") from e

    def _get_text_cache_key(self, text: str) -> str:
        """生成文本缓存key，避免长文本作为key"""
        text_md5 = hashlib.md5(text.encode("utf-8")).hexdigest()
        return f"{EMBED_CACHE_PREFIX}{text_md5}"

    @retry(
        stop=stop_after_attempt(RETRY_TIMES),
        wait=wait_fixed(RETRY_WAIT),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda s: edu_rag_logger.warning(f"向量化失败，第{s.attempt_number}次重试")
    )
    def encode_text(self, text: str) -> List[float]:
        """单文本编码"""
        # 先查缓存
        cache_key = self._get_text_cache_key(text)
        cache_vec = redis_client.get(cache_key)
        if cache_vec:
            # 缓存命中：Redis存储的是逗号拼接的字符串，转回float浮点数组
            vec = [float(x) for x in cache_vec.split(",")]
            return vec

        # 缓存无数据，生成向量
        vec = self.model.encode(text).tolist()
        # 写入缓存
        vec_str = ",".join([str(v) for v in vec])
        redis_client.set(cache_key, vec_str, expire=EMBED_CACHE_EXPIRE)
        return vec

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量文本编码"""
        vec_list = []           # 最终要返回的向量总列表
        no_cache_texts = []     # 未命中缓存、需要跑模型推理的文本
        no_cache_idx = []       # 未命中文本在原列表中的下标，用于回填结果

        # 1. 遍历所有文本，逐个查Redis缓存，拆分命中/未命中数据
        for idx, text in enumerate(texts):
            ck = self._get_text_cache_key(text)
            cache_val = redis_client.get(ck)

            if cache_val:
                # 缓存命中：解析向量放入结果列表对应位置
                vec = [float(x) for x in cache_val.split(",")]
                vec_list.append(vec)
            else:
                # 缓存未命中：先占位None，记录文本+下标
                vec_list.append(None)
                no_cache_texts.append(text)
                no_cache_idx.append(idx)

        # 2. 存在未缓存文本，批量调用模型一次性推理
        if no_cache_texts:
            edu_rag_logger.info(f"批量向量化，共{len(no_cache_texts)}条未缓存文本")
            batch_vecs = self.model.encode(no_cache_texts).tolist()

            # 3. 把批量推理结果回填到总列表，并逐个写入Redis缓存
            for i, text in enumerate(no_cache_texts):
                vec = batch_vecs[i]
                pos = no_cache_idx[i]   # 获取该文本原始下标
                vec_list[pos] = vec     # 回填到结果列表对应位置

                # 写入缓存
                ck = self._get_text_cache_key(text)
                vec_str = ",".join(str(v) for v in vec)
                redis_client.set(ck, vec_str, expire=EMBED_CACHE_EXPIRE)
        return vec_list


bge_embedder = BgeLocalEmbedder()