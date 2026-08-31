from string import Template

class PromptTemplateManager:
    # 系统角色指令
    SYSTEM_PROMPT = """
你是专业教育知识库答疑助手，严格遵守以下强制规则：
1. 优先精读全部【参考上下文】，只要文本中出现和用户问题相关的名词、结构、概念，就视为存在有效资料，必须提取内容作答；
2. 用户询问某个模型/结构组成时，只要上下文提到该模型的模块、层、组件，就整理分点输出；
3. 只有上下文从头到尾完全不包含相关概念，才允许回复：知识库暂无相关内容，无法解答；
4. 禁止主动判定“无关”，优先提取匹配知识点；回答通俗易懂、条理清晰，严禁编造不存在信息。
"""

    # RAG问答模板
    RAG_QA_PROMPT = Template("""
【参考上下文】
$context
【用户问题】
$question
""")

    @staticmethod
    def build_user_prompt(context: str, question: str) -> str:
        return PromptTemplateManager.RAG_QA_PROMPT.substitute(
            context=context,
            question=question
        )

prompt_manager = PromptTemplateManager()