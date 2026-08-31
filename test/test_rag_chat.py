from src.rag_chat.rag_chain import rag_chain
from src.common.logger_setup import edu_rag_logger

if __name__ == "__main__":
    question = "Transformer是什么？"
    edu_rag_logger.info(f"用户提问：{question}")
    ans = rag_chain.chat(question)
    print("="*60)
    print("AI回答：")
    print(ans)
    print("="*60)