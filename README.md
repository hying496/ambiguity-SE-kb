# 中文软件工程消歧知识库

本项目旨在构建一个高质量的、专门服务于消歧任务的中文软件工程知识库，通过RAG（检索增强生成）技术为消歧Agent提供推理所需的知识支持。

## 项目概述

知识库采用四层架构设计：

1. **规则层**：语言学消歧规则（指代、句法、词汇、分词等）
2. **术语层**：软件工程标准术语（多义词定义、消歧线索）
3. **案例层**：典型歧义案例（完整推理过程标注）
4. **上下文层**：软件工程常识性知识

## 项目结构

```
ambiguity-SE-kb/
├── knowledge_base/          # 知识库数据
│   ├── rules/               # 规则层
│   │   ├── reference_rules.json
│   │   ├── syntax_rules.json
│   │   ├── lexical_rules.json
│   │   └── segmentation_rules.json
│   ├── terminology/         # 术语层
│   │   └── core_terms.json
│   ├── cases/               # 案例层
│   │   ├── 1.json
│   │   └── 2.json
│   └── context/             # 上下文层
│       └── domain_knowledge.json
├── rag_system/              # RAG系统代码
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── embedding.py         # 文本嵌入
│   ├── vector_db.py         # 向量数据库接口
│   ├── retriever.py         # 知识检索器
│   ├── data_loader.py       # 数据加载
│   └── main.py              # 主程序
├── tools/                   # 工具脚本
│   ├── validate_kb.py      # 知识库验证
│   └── load_kb.py          # 数据加载测试
├── docs/                    # 文档
│   ├── requirements.md      # 需求文档
│   ├── architecture.md      # 架构文档
│   └── knowledge_schema.md  # Schema定义
├── requirements.txt         # Python依赖
├── config.yaml              # 配置文件
└── README.md                # 本文档
```

## 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 启动Milvus向量数据库（使用Docker）
# Linux/Mac:
bash scripts/start_milvus.sh

# Windows:
scripts\start_milvus.bat

# 或手动启动:
docker run -d --name milvus-standalone \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest
```

### 2. 验证知识库

```bash
# 验证知识库数据格式
python tools/validate_kb.py

# 查看知识库统计信息
python tools/load_kb.py
```

### 3. 索引知识库

```bash
# 将知识库索引到向量数据库
python -m rag_system.main --mode index
```

### 4. 检索测试

```bash
# 基本检索
python -m rag_system.main --mode search --query "接口需要重新设计"

# 按歧义类型过滤检索
python -m rag_system.main --mode search --query "用户提交了需求，系统处理了它" --ambiguity-type reference
```

## 知识库格式

详细的数据格式定义请参考 [docs/knowledge_schema.md](docs/knowledge_schema.md)

### 规则示例

```json
{
  "id": "REF-001",
  "type": "reference",
  "name": "最近指代原则",
  "description": "当存在多个可能的指代对象时，优先选择距离最近的前述实体",
  "confidence_weight": 0.8,
  "metadata": {
    "ambiguity_type": "reference",
    "usage_frequency": 0.85
  }
}
```

### 术语示例

```json
{
  "id": "TERM-001",
  "term": "接口",
  "definitions": [
    {
      "domain": "软件工程",
      "definition": "定义了一组方法签名的抽象类型",
      "disambiguation_clues": ["实现", "类", "方法", "API"]
    }
  ]
}
```

## 开发计划

### Week 1-2: MVP阶段
- [x] 基础架构搭建
- [x] 知识库Schema定义
- [x] 示例数据创建
- [ ] 100个核心术语整理
- [ ] 30个标注案例

### Week 3-4: 集成阶段
- [ ] RAG系统与Agent对接
- [ ] 300个术语扩充
- [ ] 100个案例生成
- [ ] 系统集成测试

### Week 5-6: 优化阶段
- [ ] 微调实验
- [ ] 效果对比评估
- [ ] 消歧规则补充
- [ ] 质量验证

## 使用说明

### RAG系统API

```python
from rag_system.config import Config
from rag_system.retriever import KnowledgeRetriever

# 初始化
config = Config()
retriever = KnowledgeRetriever(config)

# 检索知识
results = retriever.retrieve(
    query="接口需要重新设计",
    ambiguity_type="lexical",
    knowledge_type="rule"
)

# 按推理阶段检索
results = retriever.retrieve_by_stage(
    stage="detection",  # detection/reasoning/validation
    query="用户提交了需求",
    ambiguity_type="reference"
)
```

### 知识库验证

```python
from tools.validate_kb import validate_knowledge_base

# 验证整个知识库
success = validate_knowledge_base("knowledge_base")
```

## 配置说明

主要配置项在 `config.yaml` 中：

- `vector_db`: 向量数据库配置（Milvus/Qdrant）
- `embedding`: 嵌入模型配置
- `retrieval`: 检索参数配置

## 贡献指南

1. 添加新规则：在 `knowledge_base/rules/` 对应文件中添加
2. 添加新术语：在 `knowledge_base/terminology/core_terms.json` 中添加
3. 添加新案例：在 `knowledge_base/cases/` 中创建新的JSON文件
4. 添加上下文知识：在 `knowledge_base/context/domain_knowledge.json` 中添加

### 重要：指标计算

**所有新增知识条目必须正确设置 `confidence_weight` 和 `usage_frequency`**：

- **不要随意填写数值**：这些值必须有明确的计算依据
- **参考计算标准**：详见 [docs/metrics_definition.md](docs/metrics_definition.md)
- **使用计算工具**：运行 `python tools/calculate_metrics.py` 辅助计算
- **验证指标值**：使用 `python tools/calculate_metrics.py --mode validate --file <文件路径>` 验证

所有新增数据都需要通过 `tools/validate_kb.py` 验证。

## 许可证

[待定]

## 联系方式

项目协作成员：
- 消歧Agent开发：负责协调和集成
- RAG系统开发：负责技术架构
- 知识库建设：负责内容建设

