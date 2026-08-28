import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import ConfigError
from src.common.utils import get_now_str, clean_text

edu_rag_logger.info(f"当前时间：{get_now_str()}")
raw = "  你好   \n这是\t测试文本\n\n"
edu_rag_logger.info(f"清洗前文本：{raw}")
edu_rag_logger.info(f"清洗后文本：{clean_text(raw)}")

# 模拟抛出业务异常
try:
    raise ConfigError("测试自定义配置异常")
except ConfigError as e:
    edu_rag_logger.error(f"捕获业务异常：错误码{e.code}, 信息{e.msg}")