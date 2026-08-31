import os
from src.document_parser import parse_file

if __name__ == "__main__":
    # 替换本地任意文件路径，分别测试pdf、md、docx、ppt
    test_file_path = "../tmp_minio_test/RAG.md"
    try:
        content = parse_file(test_file_path)
        print("===== 文档解析完成，提取文本内容 =====")
        print(content)
        print(f"\n文本总长度：{len(content)} 字符")
    except Exception as e:
        print(f"解析失败：{str(e)}")