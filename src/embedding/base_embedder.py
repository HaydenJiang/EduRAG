from abc import ABC, abstractmethod
from typing import List

class BaseEmbedder(ABC):
    @abstractmethod
    def encode_text(self, text: str) -> List[float]:
        """单文本生成向量"""
        pass

    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量文本生成向量"""
        pass