# 系统架构文档

## 架构概述

本系统采用分层架构设计，包含知识库层、RAG系统层和Agent接口层。

```
┌─────────────────────────────────────────┐
│          Agent接口层                    │
│  (消歧Agent调用检索接口)                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          RAG系统层                      │
│  ┌──────────┐  ┌──────────┐           │
│  │ 检索器   │  │ 嵌入模型  │           │
│  └────┬─────┘  └────┬─────┘           │
│       │             │                  │
│  ┌────▼─────────────▼─────┐           │
│  │    向量数据库          │           │
│  │  (Milvus/Qdrant)       │           │
│  └─────────────────────────┘           │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         知识库层                        │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │
│  │规则层│ │术语层│ │案例层│ │上下文│ │
│  └──────┘ └──────┘ └──────┘ └──────┘ │
└─────────────────────────────────────────┘
```

## 核心模块

### 1. 知识库层

#### 1.1 规则层 (Rules)
- **位置**: `knowledge_base/rules/`
- **格式**: JSON数组
- **内容**: 语言学消歧规则
- **文件**:
  - `reference_rules.json`: 指代消歧规则
  - `syntax_rules.json`: 句法消歧规则
  - `lexical_rules.json`: 词汇消歧规则
  - `segmentation_rules.json`: 分词消歧规则

**核心字段**: `id`, `name`, `description`, `confidence_weight`, `priority`, `examples`, `source`

#### 1.2 术语层 (Terminology)
- **位置**: `knowledge_base/terminology/`
- **格式**: JSON数组
- **内容**: 软件工程术语，主要为词汇歧义服务，展示不同语义
- **文件**: `core_terms.json`

**核心字段**: `id`, `term`, `meanings`（不同语义列表）, `frequency`, `source`

**重点**: 通过`meanings`字段清晰展示同一术语在不同领域/上下文中的不同语义。

#### 1.3 案例层 (Cases)
- **位置**: `knowledge_base/cases/`
- **格式**: 
  - 简化格式：`case_id`, `input`, `ambiguity_type`, `analysis`, `resolved`
  - case_reasoner格式：包含`contexts`, `reasoning_chain`, `entailment_tree`, `interpretations`
- **组织**:
  - `req/no_context/`: 需求工程领域（无上下文）
  - `req/with_context/`: 需求工程领域（有上下文）
  - `req_standard/`: 需求工程标准案例（case_reasoner格式，必须有上下文）
  - `general/no_context/`: 普通领域（无上下文）
  - `general/with_context/`: 普通领域（有上下文）

#### 1.4 上下文层 (Context)
- **位置**: `knowledge_base/context/`
- **格式**: JSON数组
- **内容**: 软件工程常识性知识
- **文件**: `domain_knowledge.json`

**核心字段**: `id`, `knowledge`, `description`, `confidence`, `examples`, `source`

### 2. RAG系统层

#### 2.1 数据加载模块 (`data_loader.py`)
- **功能**: 从知识库加载数据并准备索引
- **主要方法**:
  - `load_rules()`: 加载规则
  - `load_terminology()`: 加载术语
  - `load_cases()`: 加载案例
  - `load_context()`: 加载上下文
  - `prepare_for_indexing()`: 准备索引数据

#### 2.2 嵌入模块 (`embedding.py`)
- **功能**: 文本向量化
- **模型**: sentence-transformers多语言模型
- **主要方法**:
  - `encode()`: 编码文本为向量
  - `encode_query()`: 编码查询文本

#### 2.3 向量数据库模块 (`vector_db.py`)
- **功能**: 向量存储和检索
- **支持**: Milvus（已实现）、Qdrant（待实现）
- **主要方法**:
  - `create_collection()`: 创建集合
  - `insert()`: 插入向量和元数据
  - `search()`: 搜索相似向量

#### 2.4 检索器模块 (`retriever.py`)
- **功能**: 实现混合检索策略
- **主要方法**:
  - `retrieve()`: 基本检索接口
  - `retrieve_by_stage()`: 分阶段检索接口
  - `_rerank()`: 置信度重排序

#### 2.5 配置模块 (`config.py`)
- **功能**: 系统配置管理
- **配置项**: 向量数据库、嵌入模型、检索参数

## 数据流

### 索引流程

```
知识库JSON文件
    ↓
数据加载器 (data_loader.py)
    ↓
文本内容提取
    ↓
嵌入模型 (embedding.py)
    ↓
向量 + 元数据
    ↓
向量数据库 (vector_db.py)
```

### 检索流程

```
Agent查询请求
    ↓
检索器 (retriever.py)
    ↓
查询向量化 (embedding.py)
    ↓
元数据过滤 + 向量搜索 (vector_db.py)
    ↓
置信度重排序 (retriever.py)
    ↓
返回Top-K结果
```

## 检索策略

### 混合检索策略

1. **元数据过滤**：
   - 根据 `ambiguity_type` 过滤
   - 根据 `knowledge_type` 过滤

2. **向量相似度匹配**：
   - 使用L2距离或余弦相似度
   - 返回top-k相似结果

3. **置信度重排序**：
   - 综合相似度分数和置信度权重
   - `final_score = similarity_score * confidence_weight`

### 分阶段检索

| 推理阶段 | 主要检索类型 | 说明 |
|---------|------------|------|
| detection | rule | 歧义探测阶段，主要查规则 |
| reasoning | case, rule | 推理生成阶段，查案例和规则 |
| validation | terminology, context | 前提验证阶段，查术语和常识 |

## 技术栈

### 向量数据库
- **Milvus**: 主要支持（已实现）
- **Qdrant**: 备选方案（待实现）

### 嵌入模型
- **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**
  - 支持多语言（包括中文）
  - 向量维度：384
  - 适合语义相似度计算

### Python依赖
- `numpy`: 数值计算
- `sentence-transformers`: 文本嵌入
- `pymilvus`: Milvus客户端
- `torch`: 深度学习框架


