import os
from typing import Dict, Type
from src.document_parser.base_parser import BaseDocumentParser
from src.document_parser.txt_parser import TxtMdParser
from src.document_parser.pdf_parser import PdfParser
from src.document_parser.docx_parser import DocxParser
from src.document_parser.ppt_parser import PptParser

# 后缀与解析器映射关系
PARSER_MAP: Dict[str, Type[BaseDocumentParser]] = {
    ".txt": TxtMdParser,
    ".md": TxtMdParser,
    ".pdf": PdfParser,
    ".docx": DocxParser,
    ".ppt": PptParser,
    ".pptx": PptParser
}

def get_document_parser(file_suffix: str) -> BaseDocumentParser:
    """
    根据文件后缀获取对应解析器实例
    :param file_suffix: 文件后缀，小写 如 .pdf、.docx
    :return: 解析器对象
    """
    suffix = file_suffix.lower()
    if suffix not in PARSER_MAP:
        raise ValueError(f"暂不支持解析该格式文件：{suffix}，仅支持 {list(PARSER_MAP.keys())}")
    parser_cls = PARSER_MAP[suffix]
    return parser_cls()

def parse_file(file_path: str) -> str:
    """
    一键解析文件对外统一方法
    :param file_path: 文件本地绝对路径
    :return: 提取后的完整纯文本
    """
    _, suffix = os.path.splitext(file_path)
    parser = get_document_parser(suffix)
    return parser.parse(file_path)