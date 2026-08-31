import chardet
from src.document_parser.base_parser import BaseDocumentParser

class TxtMdParser(BaseDocumentParser):
    def parse(self, file_path: str) -> str:
        # 自动检测文件编码，解决Windows GBK、UTF-8乱码问题
        with open(file_path, "rb") as f:
            raw_data = f.read()
        detect_result = chardet.detect(raw_data)
        encoding = detect_result["encoding"] or "utf-8"

        # 读取文本
        content = raw_data.decode(encoding, errors="ignore")
        # 简单文本清洗：去除过多空行、首尾空格
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        pure_text = "\n".join(lines)
        return pure_text