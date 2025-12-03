"""
知识库数据加载模块
"""
import json
import os
from typing import List, Dict, Any
import numpy as np
from .embedding import EmbeddingModel
from .config import Config

class KnowledgeBaseLoader:
    """知识库加载器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embedding_model = EmbeddingModel(config.embedding)
        self.kb_path = config.knowledge_base_path
    
    def load_rules(self) -> List[Dict[str, Any]]:
        """加载规则数据"""
        rules = []
        rules_dir = os.path.join(self.kb_path, "rules")
        
        for filename in os.listdir(rules_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(rules_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    rule_list = json.load(f)
                    rules.extend(rule_list)
        
        return rules
    
    def load_terminology(self) -> List[Dict[str, Any]]:
        """加载术语数据"""
        terms = []
        terms_file = os.path.join(self.kb_path, "terminology", "core_terms.json")
        
        if os.path.exists(terms_file):
            with open(terms_file, "r", encoding="utf-8") as f:
                terms = json.load(f)
        
        return terms
    
    def load_cases(self) -> List[Dict[str, Any]]:
        """加载案例数据"""
        cases = []
        cases_dir = os.path.join(self.kb_path, "cases")
        
        for filename in os.listdir(cases_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(cases_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    case = json.load(f)
                    cases.append(case)
        
        return cases
    
    def load_context(self) -> List[Dict[str, Any]]:
        """加载上下文知识"""
        context = []
        context_file = os.path.join(self.kb_path, "context", "domain_knowledge.json")
        
        if os.path.exists(context_file):
            with open(context_file, "r", encoding="utf-8") as f:
                context = json.load(f)
        
        return context
    
    def prepare_for_indexing(self) -> tuple:
        """
        准备索引数据
        
        Returns:
            (vectors, metadata_list) 元组
        """
        all_knowledge = []
        
        # 加载规则
        rules = self.load_rules()
        for rule in rules:
            content = f"{rule.get('name', '')} {rule.get('description', '')}"
            all_knowledge.append({
                "content": content,
                "knowledge_type": "rule",
                "ambiguity_type": rule.get("metadata", {}).get("ambiguity_type", ""),
                "confidence_weight": rule.get("confidence_weight", 0.5),
                "metadata": rule
            })
        
        # 加载术语
        terms = self.load_terminology()
        for term in terms:
            for definition in term.get("definitions", []):
                content = f"{term.get('term', '')} {definition.get('definition', '')}"
                all_knowledge.append({
                    "content": content,
                    "knowledge_type": "terminology",
                    "ambiguity_type": term.get("ambiguity_type", ""),
                    "confidence_weight": definition.get("confidence", 0.5),
                    "metadata": {
                        "term": term.get("term"),
                        "definition": definition
                    }
                })
        
        # 加载案例
        cases = self.load_cases()
        for case in cases:
            content = f"{case.get('sentence', '')} {case.get('ambiguity_description', '')}"
            all_knowledge.append({
                "content": content,
                "knowledge_type": "case",
                "ambiguity_type": case.get("metadata", {}).get("ambiguity_type", ""),
                "confidence_weight": 0.8,  # 案例默认置信度
                "metadata": case
            })
        
        # 加载上下文
        context_list = self.load_context()
        for ctx in context_list:
            content = f"{ctx.get('knowledge', '')} {ctx.get('description', '')}"
            all_knowledge.append({
                "content": content,
                "knowledge_type": "context",
                "ambiguity_type": "",
                "confidence_weight": ctx.get("confidence", 0.5),
                "metadata": ctx
            })
        
        # 生成向量
        texts = [item["content"] for item in all_knowledge]
        vectors = self.embedding_model.encode(texts)
        
        # 准备元数据
        metadata_list = [
            {
                "knowledge_type": item["knowledge_type"],
                "ambiguity_type": item["ambiguity_type"],
                "confidence_weight": item["confidence_weight"],
                "content": item["content"],
                "metadata": item["metadata"]
            }
            for item in all_knowledge
        ]
        
        return vectors, metadata_list


