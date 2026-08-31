from src.embedding.bge_embedder import bge_embedder
from src.database.milvus_client import milvus_client
from src.retrieval.reranker import reranker
from .prompt_template import prompt_manager
from .llm_client import llm_client
from src.common.logger_setup import edu_rag_logger


class EduRAGChain:
    def retrieve_context(self, query: str, top_k=5) -> str:
        # 向量检索
        embedding = bge_embedder.encode_text(query)
        results = milvus_client.search_similar(embedding, top_k=top_k)
        context_list = []
        for hit_group in results:
            for hit in hit_group:
                text = hit.entity.get("text", "")
                if text:
                    context_list.append(text)

        # =====新增Rerank重排逻辑=====
        rerank_result = reranker.rerank(query, context_list)
        # 重排后只取前3条最相关片段
        top_rerank_texts = [item[0] for item in rerank_result[:3]]
        edu_rag_logger.info(f"向量召回{len(context_list)}条，重排筛选后保留{len(top_rerank_texts)}条")

        full_context = "\n\n====文档片段====\n\n".join(top_rerank_texts)
        return full_context

    def chat(self, user_query: str) -> str:
        context = self.retrieve_context(user_query)
        user_prompt = prompt_manager.build_user_prompt(context=context, question=user_query)
        system_msg = prompt_manager.SYSTEM_PROMPT

        answer = llm_client.chat(system_prompt=system_msg, user_prompt=user_prompt)
        return answer


rag_chain = EduRAGChain()