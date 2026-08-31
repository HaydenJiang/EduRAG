from PyPDF2 import PdfReader
from src.document_parser.base_parser import BaseDocumentParser

class PdfParser(BaseDocumentParser):
    def parse(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        full_text = []
        # 逐页提取文字
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text.append(page_text.strip())
        # 合并所有页面文本
        content = "\n".join(full_text)
        # 清洗换行冗余
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return "\n".join(lines)