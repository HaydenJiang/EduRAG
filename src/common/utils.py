import os
import re
from datetime import datetime

def get_now_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前格式化时间字符串"""
    return datetime.now().strftime(fmt)

def clean_text(raw_text: str) -> str:
    """文本清洗：去除多余空格、换行、特殊不可见字符，用于知识库预处理"""
    # 去除换行、制表符
    text = re.sub(r'[\n\t\r]', "", raw_text)
    # 多个空格压缩为单个
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def safe_mkdir(path: str):
    """安全创建文件夹，防止重复创建报错"""
    if not os.path.exists(path):
        os.makedirs(path)