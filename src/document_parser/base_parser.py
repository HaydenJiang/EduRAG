from abc import ABC, abstractmethod

class BaseDocumentParser(ABC):
    """所有文档解析器统一抽象父类"""

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """
        解析文档，返回纯净完整文本
        :param file_path: 本地文件绝对路径
        :return: 去除冗余格式后的纯文本字符串
        """
        pass