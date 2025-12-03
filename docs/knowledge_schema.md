# 知识库Schema定义

本文档定义了知识库中各类知识的JSON格式规范。

## 1. 规则层 (Rules)

规则层包含消歧规则，格式统一简化。

```json
{
  "id": "REF-001",
  "name": "最近指代原则",
  "description": "当存在多个可能的指代对象时，优先选择距离最近的前述实体",
  "confidence_weight": 0.85,
  "priority": 1,
  "examples": [
    {
      "sentence": "用户提交了需求，系统处理了它。",
      "ambiguous_element": "它",
      "resolution": "它指代'需求'（最近的前述实体）"
    }
  ],
  "source": "linguistic_principle"
}
```

### 字段说明

- `id`: 规则唯一标识
- `name`: 规则名称
- `description`: 规则描述
- `confidence_weight`: 置信度权重（0.0-1.0）
- `priority`: 优先级（1最高）
- `examples`: 示例列表
  - `sentence`: 包含歧义的句子
  - `ambiguous_element`: 歧义元素
  - `resolution`: 消歧结果
- `source`: 来源类型

## 2. 术语层 (Terminology)

术语层主要为词汇歧义服务，重点展示不同语义。

```json
{
  "id": "TERM-001",
  "term": "接口",
  "meanings": [
    {
      "domain": "软件工程",
      "semantic": "定义了一组方法签名的抽象类型，用于规范类的行为",
      "disambiguation_clues": ["实现", "类", "方法", "API", "定义"],
      "examples": [
        "用户接口定义了登录方法",
        "系统需要实现这个接口"
      ],
      "confidence": 0.90
    },
    {
      "domain": "硬件",
      "semantic": "连接不同硬件设备的物理或逻辑连接点",
      "disambiguation_clues": ["硬件", "设备", "连接", "端口", "USB"],
      "examples": [
        "USB接口连接外部设备",
        "网络接口配置"
      ],
      "confidence": 0.90
    }
  ],
  "frequency": 0.95,
  "source": "domain_terminology"
}
```

### 字段说明

- `id`: 术语唯一标识
- `term`: 术语词
- `meanings`: 不同语义列表（核心字段）
  - `domain`: 所属领域
  - `semantic`: 语义定义
  - `disambiguation_clues`: 消歧线索（关键词）
  - `examples`: 例句
  - `confidence`: 该语义的置信度
- `frequency`: 术语出现频率（0.0-1.0）
- `source`: 来源类型

**重点**：术语层主要服务于词汇歧义，通过`meanings`字段清晰展示同一术语在不同领域/上下文中的不同语义。

## 3. 案例层 (Cases)

案例使用统一的简化格式，包含5个核心字段。

详细格式定义请参考 [案例Schema文档](case_schema.md)

### 3.1 统一格式

```json
{
  "case_id": "case_001",
  "input": "原始输入（句子或段落）",
  "ambiguity_type": "歧义类型",
  "analysis": "歧义分析过程（文本描述）",
  "resolved": "消歧后的句子"
}
```

### 3.2 字段说明

- `input`: 原始输入
  - **句子**：无上下文的单个句子（req和general文件夹）
  - **段落**：包含上下文的段落（req_standard文件夹必须使用段落）
- `ambiguity_type`: 歧义类型（如"多义词歧义"、"指代歧义"、"结构歧义"等）
- `analysis`: 歧义分析过程，文本描述
- `resolved`: 消歧后的句子

### 3.3 文件组织

- `req/`: 需求工程领域案例（无上下文，input是句子）
- `req_standard/`: 需求工程领域标准案例（必须有上下文，input是段落）
- `general/`: 普通领域案例（无上下文，input是句子）

## 4. 上下文层 (Context Knowledge)

上下文层包含软件工程领域的常识性知识。

```json
{
  "id": "CTX-001",
  "knowledge": "需求分析在设计之前",
  "description": "软件工程生命周期中，需求分析阶段通常在设计阶段之前进行",
  "confidence": 0.95,
  "examples": [
    "在需求分析完成后，我们开始系统设计",
    "设计阶段需要参考需求分析的结果"
  ],
  "source": "domain_expertise"
}
```

### 字段说明

- `id`: 知识唯一标识
- `knowledge`: 知识内容（简洁表述）
- `description`: 详细描述
- `confidence`: 置信度（0.0-1.0）
- `examples`: 示例列表
- `source`: 来源类型

## 指标说明

所有知识条目的指标赋值标准请参考 [指标定义文档](metrics_definition.md)

- `confidence_weight`: 置信度权重（规则）
- `confidence`: 置信度（术语语义、上下文知识）
- `frequency`: 频率（术语）
- `priority`: 优先级（规则）
