"""
知识检索模块 - 实现混合检索策略
"""
from typing import List, Dict, Any, Optional
import numpy as np
from .embedding import EmbeddingModel
from .vector_db import VectorDB
from .config import Config, RetrievalConfig

class KnowledgeRetriever:
    """知识检索器 - 实现混合检索策略"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embedding_model = EmbeddingModel(config.embedding)
        self.vector_db = None  # 延迟初始化
    
    def initialize_db(self):
        """初始化向量数据库"""
        from .vector_db import create_vector_db
        self.vector_db = create_vector_db(self.config.vector_db)
        self.vector_db.create_collection(
            self.config.vector_db.collection_name,
            self.config.vector_db.dimension
        )
    
    def retrieve(self, 
                 query: str,
                 ambiguity_type: Optional[str] = None,
                 knowledge_type: Optional[str] = None,
                 top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        检索相关知识
        
        Args:
            query: 查询文本
            ambiguity_type: 歧义类型过滤 (reference/syntax/lexical/segmentation)
            knowledge_type: 知识类型过滤 (rule/terminology/case/context)
            top_k: 返回结果数量
            
        Returns:
            检索结果列表，每个结果包含score、content、metadata等字段
        """
        if self.vector_db is None:
            self.initialize_db()
        
        # 编码查询
        query_vector = self.embedding_model.encode_query(query)
        
        # 构建过滤条件
        filter_dict = {}
        if ambiguity_type:
            filter_dict["ambiguity_type"] = ambiguity_type
        if knowledge_type:
            filter_dict["knowledge_type"] = knowledge_type
        
        # 执行检索
        top_k = top_k or self.config.retrieval.top_k
        results = self.vector_db.search(query_vector, top_k, filter_dict)
        
        # 重排序（按置信度权重）
        if self.config.retrieval.enable_rerank:
            results = self._rerank(results)
        
        # 过滤低分结果
        results = [
            r for r in results 
            if r["score"] >= self.config.retrieval.score_threshold
        ]
        
        return results
    
    def _rerank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        根据置信度权重重排序
        
        Args:
            results: 检索结果列表
            
        Returns:
            重排序后的结果列表
        """
        # 综合相似度分数和置信度权重
        for result in results:
            similarity_score = result["score"]
            confidence_weight = result.get("confidence_weight", 0.5)
            # 综合分数 = 相似度 * 置信度权重
            result["final_score"] = similarity_score * confidence_weight
        
        # 按综合分数排序
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results
    
    def retrieve_by_stage(self, 
                         stage: str,
                         query: str,
                         ambiguity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        根据推理阶段检索知识
        
        Args:
            stage: 推理阶段 (detection/reasoning/validation)
            query: 查询文本
            ambiguity_type: 歧义类型
            
        Returns:
            检索结果列表
        """
        # 不同阶段检索不同类型的知识
        stage_mapping = {
            "detection": "rule",  # 歧义探测阶段主要查规则
            "reasoning": "case",  # 推理生成阶段主要查案例和规则
            "validation": "terminology"  # 前提验证阶段主要查术语和常识
        }
        
        knowledge_type = stage_mapping.get(stage, None)
        return self.retrieve(query, ambiguity_type, knowledge_type)


