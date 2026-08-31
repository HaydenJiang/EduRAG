import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.document_parser import parse_file
from src.text_splitter import recursive_splitter
from src.embedding import bge_embedder
from src.common.logger_setup import edu_rag_logger

if __name__ == "__main__":
    # 1.解析文档
    file_path = "../tmp_minio_test/RAG.md"
    full_text = parse_file(file_path)
    # 2.文本分片
    chunks = recursive_splitter.RecursiveCharSplitter.split_text(full_text)
    edu_rag_logger.info(f"分片总数：{len(chunks)}")
    # 3.批量生成向量
    vectors = bge_embedder.encode_batch(chunks)
    edu_rag_logger.info(f"向量生成完成，单条维度：{len(vectors[0])}")

    # 4.二次读取测试缓存
    vectors2 = bge_embedder.encode_batch(chunks)
    edu_rag_logger.info("缓存读取向量完成，无重复计算")