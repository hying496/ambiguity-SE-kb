"""
知识库数据验证工具
验证JSON文件是否符合Schema定义
"""
import json
import os
import sys
from pathlib import Path

def validate_rule(rule: dict) -> tuple[bool, str]:
    """验证规则数据"""
    required_fields = ["id", "type", "name", "description", "confidence_weight", "metadata"]
    for field in required_fields:
        if field not in rule:
            return False, f"缺少必需字段: {field}"
    
    if rule["type"] not in ["reference", "syntax", "lexical", "segmentation"]:
        return False, f"无效的类型: {rule['type']}"
    
    if "ambiguity_type" not in rule.get("metadata", {}):
        return False, "metadata中缺少ambiguity_type"
    
    return True, ""

def validate_term(term: dict) -> tuple[bool, str]:
    """验证术语数据"""
    required_fields = ["id", "term", "definitions", "ambiguity_type", "metadata"]
    for field in required_fields:
        if field not in term:
            return False, f"缺少必需字段: {field}"
    
    if not isinstance(term["definitions"], list) or len(term["definitions"]) == 0:
        return False, "definitions必须是非空列表"
    
    for i, definition in enumerate(term["definitions"]):
        def_required = ["id", "domain", "definition", "keywords", "disambiguation_clues", "examples", "confidence"]
        for field in def_required:
            if field not in definition:
                return False, f"定义 {i} 缺少必需字段: {field}"
    
    return True, ""

def validate_case(case: dict) -> tuple[bool, str]:
    """验证案例数据"""
    required_fields = ["id", "type", "sentence", "ambiguity_description", "reasoning_paths", "metadata"]
    for field in required_fields:
        if field not in case:
            return False, f"缺少必需字段: {field}"
    
    if not isinstance(case["reasoning_paths"], list) or len(case["reasoning_paths"]) == 0:
        return False, "reasoning_paths必须是非空列表"
    
    return True, ""

def validate_context(ctx: dict) -> tuple[bool, str]:
    """验证上下文知识"""
    required_fields = ["id", "type", "knowledge", "description", "confidence", "metadata"]
    for field in required_fields:
        if field not in ctx:
            return False, f"缺少必需字段: {field}"
    
    return True, ""

def validate_file(filepath: str) -> tuple[bool, list[str]]:
    """验证单个JSON文件"""
    errors = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 判断文件类型
        if "rules" in filepath:
            if isinstance(data, list):
                for i, rule in enumerate(data):
                    valid, error = validate_rule(rule)
                    if not valid:
                        errors.append(f"规则 {i}: {error}")
            else:
                errors.append("规则文件应该是JSON数组")
        
        elif "terminology" in filepath or "terms" in filepath:
            if isinstance(data, list):
                for i, term in enumerate(data):
                    valid, error = validate_term(term)
                    if not valid:
                        errors.append(f"术语 {i}: {error}")
            else:
                errors.append("术语文件应该是JSON数组")
        
        elif "cases" in filepath:
            valid, error = validate_case(data)
            if not valid:
                errors.append(f"案例: {error}")
        
        elif "context" in filepath:
            if isinstance(data, list):
                for i, ctx in enumerate(data):
                    valid, error = validate_context(ctx)
                    if not valid:
                        errors.append(f"上下文 {i}: {error}")
            else:
                errors.append("上下文文件应该是JSON数组")
        
    except json.JSONDecodeError as e:
        errors.append(f"JSON解析错误: {e}")
    except Exception as e:
        errors.append(f"文件读取错误: {e}")
    
    return len(errors) == 0, errors

def validate_knowledge_base(kb_path: str = "knowledge_base"):
    """验证整个知识库"""
    kb_path = Path(kb_path)
    if not kb_path.exists():
        print(f"错误: 知识库路径不存在: {kb_path}")
        return False
    
    all_errors = {}
    
    # 验证规则
    rules_dir = kb_path / "rules"
    if rules_dir.exists():
        for file in rules_dir.glob("*.json"):
            valid, errors = validate_file(str(file))
            if not valid:
                all_errors[str(file)] = errors
    
    # 验证术语
    terms_file = kb_path / "terminology" / "core_terms.json"
    if terms_file.exists():
        valid, errors = validate_file(str(terms_file))
        if not valid:
            all_errors[str(terms_file)] = errors
    
    # 验证案例
    cases_dir = kb_path / "cases"
    if cases_dir.exists():
        for file in cases_dir.glob("*.json"):
            valid, errors = validate_file(str(file))
            if not valid:
                all_errors[str(file)] = errors
    
    # 验证上下文
    context_file = kb_path / "context" / "domain_knowledge.json"
    if context_file.exists():
        valid, errors = validate_file(str(context_file))
        if not valid:
            all_errors[str(context_file)] = errors
    
    # 输出结果
    if all_errors:
        print("验证失败！发现以下错误:\n")
        for filepath, errors in all_errors.items():
            print(f"{filepath}:")
            for error in errors:
                print(f"  - {error}")
            print()
        return False
    else:
        print("✓ 所有知识库文件验证通过！")
        return True

if __name__ == "__main__":
    kb_path = sys.argv[1] if len(sys.argv) > 1 else "knowledge_base"
    success = validate_knowledge_base(kb_path)
    sys.exit(0 if success else 1)


