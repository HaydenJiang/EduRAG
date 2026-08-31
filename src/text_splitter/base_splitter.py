from abc import ABC, abstractmethod
from typing import List

class BaseTextSplitter(ABC):
    """文本分片统一抽象类"""
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size        # 单个文本块最大字符长度
        self.chunk_overlap = chunk_overlap  # 相邻两个块之间重叠字符数量

    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """
        输入完整文本，返回分段后的文本列表
        """
        pass