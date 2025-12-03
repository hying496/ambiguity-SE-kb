"""
向量数据库接口模块
支持Milvus和Qdrant
"""
from typing import List, Dict, Any, Optional
import numpy as np
from abc import ABC, abstractmethod
from .config import VectorDBConfig

class VectorDB(ABC):
    """向量数据库抽象基类"""
    
    @abstractmethod
    def create_collection(self, collection_name: str, dimension: int):
        """创建集合"""
        pass
    
    @abstractmethod
    def insert(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """插入向量和元数据"""
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, top_k: int, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str):
        """删除集合"""
        pass

class MilvusDB(VectorDB):
    """Milvus向量数据库实现"""
    
    def __init__(self, config: VectorDBConfig):
        self.config = config
        try:
            from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
            self.connections = connections
            self.Collection = Collection
            self.FieldSchema = FieldSchema
            self.CollectionSchema = CollectionSchema
            self.DataType = DataType
            self.utility = utility
        except ImportError:
            raise ImportError("请安装pymilvus: pip install pymilvus")
        
        # 连接到Milvus
        self.connections.connect(
            alias="default",
            host=config.host,
            port=config.port
        )
        self.collection = None
    
    def create_collection(self, collection_name: str, dimension: int):
        """创建Milvus集合"""
        if self.utility.has_collection(collection_name):
            self.collection = self.Collection(collection_name)
            return
        
        # 定义schema
        fields = [
            self.FieldSchema(name="id", dtype=self.DataType.INT64, is_primary=True, auto_id=True),
            self.FieldSchema(name="vector", dtype=self.DataType.FLOAT_VECTOR, dim=dimension),
            self.FieldSchema(name="knowledge_type", dtype=self.DataType.VARCHAR, max_length=50),
            self.FieldSchema(name="ambiguity_type", dtype=self.DataType.VARCHAR, max_length=50),
            self.FieldSchema(name="confidence_weight", dtype=self.DataType.FLOAT),
            self.FieldSchema(name="content", dtype=self.DataType.VARCHAR, max_length=10000),
            self.FieldSchema(name="metadata_json", dtype=self.DataType.VARCHAR, max_length=5000)
        ]
        
        schema = self.CollectionSchema(fields, "消歧知识库集合")
        self.collection = self.Collection(collection_name, schema)
        
        # 创建索引
        index_params = {
            "metric_type": self.config.metric_type,
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index("vector", index_params)
    
    def insert(self, vectors: np.ndarray, metadata: List[Dict[str, Any]], ids: Optional[List[str]] = None):
        """插入向量和元数据到Milvus"""
        if self.collection is None:
            raise ValueError("请先创建集合")
        
        import json
        
        entities = [
            vectors.tolist(),
            [m.get("knowledge_type", "") for m in metadata],
            [m.get("ambiguity_type", "") for m in metadata],
            [m.get("confidence_weight", 0.0) for m in metadata],
            [m.get("content", "") for m in metadata],
            [json.dumps(m.get("metadata", {}), ensure_ascii=False) for m in metadata]
        ]
        
        self.collection.insert(entities)
        self.collection.flush()
    
    def search(self, query_vector: np.ndarray, top_k: int, 
               filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """在Milvus中搜索"""
        if self.collection is None:
            raise ValueError("请先创建集合")
        
        # 构建过滤表达式
        expr = None
        if filter_dict:
            conditions = []
            if "knowledge_type" in filter_dict:
                conditions.append(f'knowledge_type == "{filter_dict["knowledge_type"]}"')
            if "ambiguity_type" in filter_dict:
                conditions.append(f'ambiguity_type == "{filter_dict["ambiguity_type"]}"')
            if conditions:
                expr = " && ".join(conditions)
        
        # 执行搜索
        search_params = {"metric_type": self.config.metric_type, "params": {"nprobe": 10}}
        results = self.collection.search(
            data=query_vector.tolist(),
            anns_field="vector",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["knowledge_type", "ambiguity_type", "confidence_weight", "content", "metadata_json"]
        )
        
        # 格式化结果
        formatted_results = []
        import json
        for hits in results:
            for hit in hits:
                # 获取实体字段
                entity = hit.entity
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "knowledge_type": entity.get("knowledge_type") if hasattr(entity, 'get') else getattr(entity, 'knowledge_type', ''),
                    "ambiguity_type": entity.get("ambiguity_type") if hasattr(entity, 'get') else getattr(entity, 'ambiguity_type', ''),
                    "confidence_weight": entity.get("confidence_weight") if hasattr(entity, 'get') else getattr(entity, 'confidence_weight', 0.0),
                    "content": entity.get("content") if hasattr(entity, 'get') else getattr(entity, 'content', ''),
                    "metadata": json.loads(entity.get("metadata_json", "{}") if hasattr(entity, 'get') else getattr(entity, 'metadata_json', '{}'))
                })
        
        return formatted_results
    
    def delete_collection(self, collection_name: str):
        """删除Milvus集合"""
        if self.utility.has_collection(collection_name):
            self.utility.drop_collection(collection_name)

def create_vector_db(config: VectorDBConfig) -> VectorDB:
    """工厂函数：根据配置创建向量数据库实例"""
    if config.db_type.lower() == "milvus":
        return MilvusDB(config)
    elif config.db_type.lower() == "qdrant":
        # TODO: 实现QdrantDB
        raise NotImplementedError("Qdrant支持待实现")
    else:
        raise ValueError(f"不支持的向量数据库类型: {config.db_type}")

