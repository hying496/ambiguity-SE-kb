"""
RAG系统配置文件
"""
import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class VectorDBConfig:
    """向量数据库配置"""
    db_type: str = "milvus"  # 或 "qdrant"
    host: str = "localhost"
    port: int = 19530
    collection_name: str = "ambiguity_kb"
    dimension: int = 768  # 向量维度，根据embedding模型调整
    metric_type: str = "L2"  # 距离度量类型

@dataclass
class EmbeddingConfig:
    """Embedding模型配置"""
    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    device: str = "cpu"  # 或 "cuda"
    max_length: int = 512

@dataclass
class RetrievalConfig:
    """检索配置"""
    top_k: int = 10  # 检索返回的top-k结果数
    score_threshold: float = 0.5  # 相似度阈值
    enable_rerank: bool = True  # 是否启用重排序

class Config:
    """全局配置类"""
    def __init__(self):
        self.vector_db = VectorDBConfig()
        self.embedding = EmbeddingConfig()
        self.retrieval = RetrievalConfig()
        self.knowledge_base_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "knowledge_base"
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """从字典创建配置对象"""
        config = cls()
        if "vector_db" in config_dict:
            config.vector_db = VectorDBConfig(**config_dict["vector_db"])
        if "embedding" in config_dict:
            config.embedding = EmbeddingConfig(**config_dict["embedding"])
        if "retrieval" in config_dict:
            config.retrieval = RetrievalConfig(**config_dict["retrieval"])
        return config


