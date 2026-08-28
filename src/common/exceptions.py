class BaseBizException(Exception):

    """项目业务异常基类"""
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(self.msg)

# ================= 通用异常 =================
class ConfigError(BaseBizException):
    """配置读取失败异常"""
    def __init__(self, msg: str = "配置文件读取错误"):
        super().__init__(code=10001, msg=msg)

class DatabaseConnectError(BaseBizException):
    """数据库连接失败"""
    def __init__(self, db_name: str):
        super().__init__(code=10002, msg=f"{db_name} 数据库连接失败，请检查服务状态与账号密码")

class LLMRequestError(BaseBizException):
    """大模型调用异常"""
    def __init__(self, msg: str = "通义千问接口请求失败"):
        super().__init__(code=20001, msg=msg)

class RetrievalError(BaseBizException):
    """检索召回异常"""
    def __init__(self, msg: str = "知识库检索失败"):
        super().__init__(code=30001, msg=msg)

class PipelineError(BaseBizException):
    """知识库流水线执行异常"""
    def __init__(self, msg: str):
        super().__init__(code=50001, msg=msg)


# ================= MinIO文件业务异常 =================
class FileTooLargeError(BaseBizException):
    """文件超出最大限制"""
    def __init__(self, max_size: int):
        super().__init__(code=40001, msg=f"文件最大允许{max_size}MB，超出上传限制")

class FileSuffixNotAllowedError(BaseBizException):
    """不允许的文件后缀"""
    def __init__(self, allow_suffix: str):
        super().__init__(code=40002, msg=f"仅支持上传：{allow_suffix} 格式文件")

class FileNotExistError(BaseBizException):
    """MinIO文件不存在"""
    def __init__(self):
        super().__init__(code=40003, msg="目标文件在对象存储中不存在")

class FileMd5MismatchError(BaseBizException):
    """文件MD5校验不一致，文件被篡改/损坏"""
    def __init__(self):
        super().__init__(code=40004, msg="文件MD5校验失败，文件已损坏或被篡改")