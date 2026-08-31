from src.document_parser import parse_file
from src.text_splitter import default_text_splitter

if __name__ == "__main__":
    # 读取测试文档
    file_path = "LLM基础知识.pdf"
    full_text = parse_file(file_path)

    # 文本分片
    chunk_list = default_text_splitter.split_text(full_text)

    print(f"全文总字符：{len(full_text)}")
    print(f"分片总数：{len(chunk_list)}")
    print("-" * 60)
    for idx, chunk in enumerate(chunk_list):
        print(f"【分片{idx+1} 长度{len(chunk)}】")
        print(chunk)
        print("-" * 60)