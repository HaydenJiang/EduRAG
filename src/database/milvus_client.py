from pymilvus import (
    connections,
    utility,
    Collection,
    FieldSchema,
    DataType,
    CollectionSchema
)
from src.common.config_loader import settings
from src.common.logger_setup import edu_rag_logger
from src.common.exceptions import DatabaseConnectError

class MilvusClient:
    _instance = None
    CONN_ALIAS = "edu_rag_milvus"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        milvus_cfg = settings.MILVUS
        try:
            # 建立连接
            connections.connect(
                alias=self.CONN_ALIAS,
                host=milvus_cfg["host"],
                port=milvus_cfg["port"]
            )
            # 校验连通性：改用查看集合列表判断服务通不通，替代has_connection
            utility.list_collections(using=self.CONN_ALIAS)
            edu_rag_logger.info(f"Milvus 向量库连接成功 | 集合名称：{milvus_cfg['collection']}")
            self.collection_name = milvus_cfg["collection"]
        except Exception as e:
            edu_rag_logger.error(f"Milvus连接失败：{str(e)}")
            raise DatabaseConnectError(db_name="Milvus向量数据库") from e

    def create_knowledge_collection(self, dim: int = 512):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim)
        ]
        schema = CollectionSchema(fields=fields, description="EduRAG知识库向量集合")

        # 集合存在就删除重建
        if utility.has_collection(self.collection_name, using=self.CONN_ALIAS):
            utility.drop_collection(self.collection_name, using=self.CONN_ALIAS)
            edu_rag_logger.warning(f"旧集合 {self.collection_name} 已删除")

        coll = Collection(name=self.collection_name, schema=schema, using=self.CONN_ALIAS)
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        coll.create_index(field_name="vector", index_params=index_params)
        coll.load()
        edu_rag_logger.info(f"知识库集合 {self.collection_name} 创建完成")
        return coll

    def insert_data(self, texts: list[str], vectors: list[list[float]]):
        coll = Collection(self.collection_name, using=self.CONN_ALIAS)
        data = [texts, vectors]
        insert_res = coll.insert(data)
        coll.flush()
        edu_rag_logger.info(f"插入向量数据条数：{len(texts)}")
        return insert_res

    def search_similar(self, query_vector: list[float], top_k: int = 3):
        coll = Collection(self.collection_name, using=self.CONN_ALIAS)
        coll.load()
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = coll.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=top_k,
            output_fields=["text"]
        )
        return results

    def close(self):
        connections.disconnect(alias=self.CONN_ALIAS)
        edu_rag_logger.info("Milvus 连接已断开")


milvus_client = MilvusClient()