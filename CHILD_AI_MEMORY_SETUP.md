# 🧠 子AI记忆仓库模块 - 设置指南

## 📋 概述

子AI记忆仓库（Child AI Memory Vault）是一个独立模块，用于记录和管理用户与匹配对象的互动历史，为前端 React 组件提供数据源。

---

## 🛠️ 设置步骤

### 1️⃣ 更新 Supabase 表结构

由于 `child_ai_memory` 表已存在但缺少必要的列，您需要执行以下SQL来更新表结构：

**操作步骤：**

1. 登录 Supabase Dashboard
2. 进入 SQL Editor
3. 复制并执行 `update_child_ai_memory_table.sql` 中的SQL语句

**或者直接复制以下SQL：**

```sql
-- 添加 interaction_count 列
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS interaction_count INTEGER DEFAULT 1;

-- 添加 last_interaction 列
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS last_interaction TIMESTAMP DEFAULT NOW();

-- 添加 summary 列
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS summary TEXT;

-- 添加 tags 列
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS tags TEXT[];

-- 添加 similarity 列
ALTER TABLE public.child_ai_memory 
ADD COLUMN IF NOT EXISTS similarity FLOAT;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_child_ai_memory_last_interaction 
ON public.child_ai_memory(last_interaction DESC);
```

---

### 2️⃣ 测试后端模块

执行SQL后，运行测试：

```bash
python child_ai_memory.py
```

**预期输出：**
```
🧪 测试子AI记忆仓库模块 ...
✅ Table 'child_ai_memory' already exists.
📊 正在为用户 u_demo 创建记忆...
💾 已保存新记忆：u_demo ↔ u_test1
💾 已保存新记忆：u_demo ↔ u_test2
✅ 记忆同步完成：新建 2 条，更新 0 条
```

---

### 3️⃣ 集成到前端

React 组件已保存在 `components/ChildAIMemoryVault.jsx`

**使用方法：**

```javascript
import ChildAIMemoryVault from './components/ChildAIMemoryVault';

function App() {
  return (
    <ChildAIMemoryVault userId="u_demo" />
  );
}
```

**环境变量设置（.env）：**
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
```

---

## 📊 数据流

```
child_ai_insights (洞察表)
         ↓
child_ai_memory.py (Python后端)
         ↓
child_ai_memory (记忆表) ← Supabase
         ↓
ChildAIMemoryVault.jsx (React前端)
```

---

## 🎯 功能特性

### 后端模块 (`child_ai_memory.py`)

- **自动生成摘要**：从洞察文本提取核心内容
- **标签提取**：从 shared_tags 生成可读标签列表
- **智能更新**：追踪互动次数和最后互动时间
- **批量创建**：从 child_ai_insights 批量同步记忆

### 前端组件 (`ChildAIMemoryVault.jsx`)

- **实时搜索**：按 partner_id 或关键词过滤
- **动画效果**：使用 framer-motion 流畅过渡
- **标签展示**：美观的紫色标签UI
- **时间排序**：按创建时间倒序显示

---

## 📁 项目文件

```
LynkerAI/
├── child_ai_memory.py              # 后端模块
├── components/
│   └── ChildAIMemoryVault.jsx      # React组件
├── supabase_tables_schema.sql      # 完整表结构
├── update_child_ai_memory_table.sql # 更新脚本
└── CHILD_AI_MEMORY_SETUP.md        # 本文档
```

---

## 🧪 测试验证

```bash
# 1. 更新表结构后测试
python child_ai_memory.py

# 2. 验证Supabase数据
python supabase_auto_setup.py

# 3. 检查记忆数量
python -c "from child_ai_memory import *; s=init_supabase(); m=get_user_memories('u_demo',s); print(f'找到 {len(m)} 条记忆')"
```

---

## ✅ 验证清单

- [ ] 在 Supabase Dashboard 执行了 `update_child_ai_memory_table.sql`
- [ ] `python child_ai_memory.py` 运行成功
- [ ] `child_ai_memory` 表包含测试数据
- [ ] React 组件可以读取数据
- [ ] 环境变量已配置

---

**🎉 完成设置后，子AI记忆仓库即可使用！**
