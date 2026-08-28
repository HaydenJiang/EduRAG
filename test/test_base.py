from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger

edu_rag_logger.info("===== 测试全局配置读取 =====")
edu_rag_logger.info(f"MySQL数据库名：{settings.MYSQL['database']}")
edu_rag_logger.info(f"Milvus集合名：{settings.MILVUS['collection']}")
edu_rag_logger.info(f"客服业务电话：{settings.CUSTOMER_SERVICE_PHONE}")
edu_rag_logger.info(f"通义千问KEY前20位：{settings.LLM['api_key'][:20]}...")
edu_rag_logger.info("基础公共模块加载完成！")