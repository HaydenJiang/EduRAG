from src.rag_chat.rag_chain import rag_chain

if __name__ == "__main__":
    question = "Transformer组成？"
    resp = rag_chain.chat(question)
    print("=====最终回答=====")
    print(resp)