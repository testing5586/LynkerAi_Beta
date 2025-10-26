# LKK Knowledge Base 知识库系统

## 📚 概述

LynkerAI 命理知识库 - 三层架构的智能知识管理系统

```
lkk_knowledge_base/
├── rules/          # 固定规则层（手动维护）
├── patterns/       # 演化模式层（AI自动生成）
├── case_study/     # 命例验证层（验证数据库导出）
├── retrieval_router.py   # 检索引擎
├── access_control.py     # 访问控制
└── README.md      # 本文件
```

---

## 🎯 核心设计

### 三层知识架构

| 层级 | 目录 | 来源 | 更新方式 | 状态 |
|------|------|------|----------|------|
| **固定层** | `rules/` | 手动整理经典理论 | 人工更新 | 基础层 |
| **演化层** | `patterns/` | Child AI 验证结果聚合 | Evolution Engine 定期跑 | 动态增长 |
| **命例层** | `case_study/` | user_verification_results 表 | 定期批处理脱敏导出 | 持续累积 |

### 检索策略

- **当前**：Keyword + Regex 触发 + LLM 自解释
- **未来升级路径**：case_study ≥ 2000 条时，切换到 OpenAI Embeddings

---

## 🔍 使用方法

### 1. 检索知识库

```python
from lkk_knowledge_base.retrieval_router import find_relevant_knowledge

# 查询所有类别
results = find_relevant_knowledge("婚姻宫化忌对感情的影响")

# 只查询特定类别
results = find_relevant_knowledge(
    query="财运走势", 
    categories=["rules", "patterns"],
    max_results=3
)

# 返回格式
{
    "rules": [...],         # 匹配的规则文件
    "patterns": [...],      # 匹配的统计模式
    "case_study": [...],    # 匹配的案例
    "summary": "找到 2 条规则、1 条模式、0 个案例"
}
```

### 2. 访问权限控制

```python
from lkk_knowledge_base.access_control import check_knowledge_access, AccessLevel

# 检查读权限
can_read = check_knowledge_access("pro", "patterns", "read")

# 检查写权限
can_write = check_knowledge_access("admin", "rules", "write")
```

### 权限级别

| 级别 | 可读 | 可写 |
|------|------|------|
| GUEST | 无 | 无 |
| USER | rules | 无 |
| PRO | rules + patterns | 无 |
| ADMIN | rules + patterns | rules |
| SUPERINTENDENT | 全部 | 全部 |

---

## 📂 知识库内容

### rules/ - 固定规则层

经典命理理论，手动维护：

- `bazi_core_rules.md` - 八字核心规则（子平/盲派/倪海厦）
- `ziwei_palace_rules.md` - 紫微斗数宫位规则
- `health_patterns.md` - 健康疾病规律（待添加）

### patterns/ - 演化模式层

AI 自动生成的统计规律：

- `marriage_patterns.json` - 婚姻匹配模式
- `wealth_curve_patterns.json` - 财运曲线模式
- `time_alignment_keys.json` - 真命时辰校准关键点

**生成来源**：Master AI Evolution Engine 定期分析 user_verification_results 表

### case_study/ - 命例验证层

去标识化真实案例：

- `2025_sample_case_001.json` - 示例案例（脱敏）
- ...（持续累积中）

**导出来源**：`case_study_exporter.py` 定期从数据库导出

---

## 🔧 维护指南

### 添加新规则（手动）

1. 在 `rules/` 目录创建 Markdown 文件
2. 遵循现有格式（章节结构 + 示例）
3. 提交前测试检索是否生效

### 查看知识库统计

```python
from lkk_knowledge_base.retrieval_router import get_retrieval_router

router = get_retrieval_router()
stats = router.get_stats()

print(stats)
# {'rules_count': 2, 'patterns_count': 0, 'case_study_count': 0}
```

### 导出案例（定期执行）

```bash
python lkk_knowledge_base/case_study_exporter.py --limit 100
```

---

## 🚀 集成到 AI Prompts

### Primary AI & Child AI 集成示例

```python
from lkk_knowledge_base.retrieval_router import find_relevant_knowledge

def get_enhanced_prompt(user_query: str, base_prompt: str) -> str:
    """
    为 AI prompt 注入知识库上下文
    """
    # 检索相关知识
    knowledge = find_relevant_knowledge(user_query, max_results=3)
    
    # 构建增强上下文
    context_parts = []
    
    if knowledge["rules"]:
        context_parts.append("【命理规则】")
        for rule in knowledge["rules"]:
            context_parts.append(f"- {rule['content'][:200]}...")
    
    if knowledge["patterns"]:
        context_parts.append("\n【统计规律】")
        for pattern in knowledge["patterns"]:
            context_parts.append(f"- {pattern['source']}: {pattern['matched_keywords']}")
    
    enhanced_context = "\n".join(context_parts)
    
    # 注入到 prompt
    return f"{base_prompt}\n\n===== 知识库增强 =====\n{enhanced_context}\n\n用户问题：{user_query}"
```

---

## 📊 当前统计

**最后更新**：2025-10-26

| 类别 | 数量 | 状态 |
|------|------|------|
| 规则文件 | 2 | ✅ 基础规则已就绪 |
| 统计模式 | 0 | ⏳ 等待 Evolution Engine 生成 |
| 验证案例 | 0 | ⏳ 等待数据库积累 |

---

## 🔮 未来升级路径

### 当 case_study ≥ 2000 条时

1. **切换到向量检索**：
   - 使用 OpenAI Embeddings API
   - 构建向量索引（FAISS 或 Pinecone）
   
2. **保持接口不变**：
   ```python
   # 只需替换 retrieval_router.py 内部实现
   # AI 调用方式不变
   results = find_relevant_knowledge(query)
   ```

3. **性能提升**：
   - 语义搜索更精准
   - 支持复杂推理查询
   - 跨领域知识关联

---

## ⚠️ 注意事项

1. **不暴露外部 API**：知识库仅供内部 AI 调用，不开放 REST 接口
2. **权限控制严格**：防止用户绕过验证直接查询
3. **数据脱敏**：case_study 必须去除个人标识信息
4. **定期备份**：patterns/ 和 case_study/ 需定期备份

---

**维护团队**：LynkerAI Knowledge Team  
**联系方式**：内部系统，无需外部联系
