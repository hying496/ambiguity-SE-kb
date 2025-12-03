"""
文本嵌入模块 - 将文本转换为向量表示
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from .config import EmbeddingConfig

class EmbeddingModel:
    """文本嵌入模型封装"""
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.model = SentenceTransformer(
            config.model_name,
            device=config.device
        )
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        将文本编码为向量
        
        Args:
            texts: 单个文本或文本列表
            
        Returns:
            向量数组，shape为(len(texts), dimension)
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """
        编码查询文本（用于检索）
        
        Args:
            query: 查询文本
            
        Returns:
            查询向量，shape为(1, dimension)
        """
        return self.encode(query)


