from typing import Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import LLMRequestError

# 从统一配置读取大模型参数
LLM_API_KEY = settings.LLM["api_key"]
LLM_BASE_URL = settings.LLM["base_url"]
LLM_MODEL = settings.LLM["model_name"]

# 重试配置
RETRY_TIMES = 2
RETRY_WAIT = 1

# 初始化OpenAI客户端（兼容阿里云通义千问兼容接口）
client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)

class QwenLLMClient:
    @retry(
        stop=stop_after_attempt(RETRY_TIMES),
        wait=wait_fixed(RETRY_WAIT),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda s: edu_rag_logger.warning(f"LLM调用失败，第{s.attempt_number}次重试")
    )
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        try:
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            answer = resp.choices[0].message.content.strip()
            edu_rag_logger.info("LLM问答生成完成")
            return answer
        except Exception as e:
            edu_rag_logger.error(f"LLM调用异常：{str(e)}")
            raise LLMRequestError(msg=f"大模型请求失败：{str(e)}") from e

llm_client = QwenLLMClient()