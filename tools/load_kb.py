"""
知识库加载工具 - 用于测试数据加载
"""
import json
import os
import sys
from pathlib import Path

def load_all_knowledge(kb_path: str = "knowledge_base"):
    """加载所有知识库数据"""
    kb_path = Path(kb_path)
    knowledge = {
        "rules": [],
        "terminology": [],
        "cases": [],
        "context": []
    }
    
    # 加载规则
    rules_dir = kb_path / "rules"
    if rules_dir.exists():
        for file in rules_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                rules = json.load(f)
                knowledge["rules"].extend(rules)
    
    # 加载术语
    terms_file = kb_path / "terminology" / "core_terms.json"
    if terms_file.exists():
        with open(terms_file, "r", encoding="utf-8") as f:
            knowledge["terminology"] = json.load(f)
    
    # 加载案例
    cases_dir = kb_path / "cases"
    if cases_dir.exists():
        for file in cases_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                case = json.load(f)
                knowledge["cases"].append(case)
    
    # 加载上下文
    context_file = kb_path / "context" / "domain_knowledge.json"
    if context_file.exists():
        with open(context_file, "r", encoding="utf-8") as f:
            knowledge["context"] = json.load(f)
    
    return knowledge

def print_statistics(knowledge: dict):
    """打印知识库统计信息"""
    print("=" * 50)
    print("知识库统计信息")
    print("=" * 50)
    print(f"规则数量: {len(knowledge['rules'])}")
    print(f"术语数量: {len(knowledge['terminology'])}")
    print(f"案例数量: {len(knowledge['cases'])}")
    print(f"上下文知识数量: {len(knowledge['context'])}")
    print()
    
    # 按类型统计规则
    rule_types = {}
    for rule in knowledge["rules"]:
        rule_type = rule.get("type", "unknown")
        rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
    
    print("规则类型分布:")
    for rule_type, count in rule_types.items():
        print(f"  {rule_type}: {count}")
    print()
    
    # 按歧义类型统计
    ambiguity_types = {}
    for rule in knowledge["rules"]:
        amb_type = rule.get("metadata", {}).get("ambiguity_type", "unknown")
        ambiguity_types[amb_type] = ambiguity_types.get(amb_type, 0) + 1
    
    print("歧义类型分布:")
    for amb_type, count in ambiguity_types.items():
        print(f"  {amb_type}: {count}")

if __name__ == "__main__":
    kb_path = sys.argv[1] if len(sys.argv) > 1 else "knowledge_base"
    knowledge = load_all_knowledge(kb_path)
    print_statistics(knowledge)


