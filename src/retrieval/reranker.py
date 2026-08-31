import logging
from typing import List, Tuple
from sentence_transformers import CrossEncoder
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger


class BgeReranker:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if BgeReranker._initialized:
            return

        self.model_path = settings.RERANK_MODEL_PATH
        self.threshold = settings.RERANK_SCORE_THRESHOLD
        self.model: CrossEncoder = None
        self._load_model()
        BgeReranker._initialized = True

    def _load_model(self):
        """加载本地重排模型"""
        try:
            edu_rag_logger.info(f"加载本地Rerank模型: {self.model_path}")
            self.model = CrossEncoder(self.model_path)
            edu_rag_logger.info("Rerank模型加载成功")
        except Exception as e:
            edu_rag_logger.error(f"Rerank模型加载失败: {str(e)}")
            raise

    def rerank(self, query: str, text_list: List[str]) -> List[Tuple[str, float]]:
        """
        对召回文本重排序
        :param query: 用户问题
        :param text_list: 向量检索得到的文本列表
        :return: [(文本,相关性分数)] 按分数从高到低排序
        """
        if not text_list:
            return []

        # 构造query-文本配对
        pairs = [(query, text) for text in text_list]
        scores = self.model.predict(pairs)

        text_score_pairs = list(zip(text_list, scores))
        # 分数降序排列
        text_score_pairs.sort(key=lambda x: x[1], reverse=True)
        # 过滤低于阈值的文本
        filter_result = [(t, s) for t, s in text_score_pairs if s >= self.threshold]
        return filter_result


reranker = BgeReranker()