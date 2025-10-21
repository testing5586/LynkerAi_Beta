# 🧠 Lynker Master Vault（灵客总AI知识仓库）

**版本：** 1.0.0  
**创建日期：** 2025-10-21

---

## 📋 概述

Lynker Master Vault 是一个智能文档管理系统，专为 LynkerAI 项目设计。它自动分类、索引和检索项目文档，为 AI 助手提供结构化的知识上下文。

---

## 📁 目录结构

```
lynker_master_vault/
├── project_docs/       # 项目文档（UI、设计、前端）
├── dev_brainstorm/     # 开发思路（AI、命理、玄学）
├── api_docs/           # API 文档（后端、认证、数据库）
├── memory/             # 记忆存储（保留用于未来功能）
├── index.yaml          # 全局索引文件
└── README.md           # 本文档
```

---

## 🚀 快速开始

### 1. 导入文档

```bash
# 导入单个文档
python master_ai_importer.py import <文件路径>

# 示例
python master_ai_importer.py import OAUTH_CALLBACK_GUIDE.md
```

**自动分类规则：**
- 包含 `ui`, `design`, `dashboard`, `client`, `frontend` → `project_docs`
- 包含 `api`, `auth`, `supabase`, `drive`, `oauth`, `backend` → `api_docs`
- 包含 `ai`, `命理`, `同命`, `玄学`, `太玄`, `铁板` → `dev_brainstorm`

### 2. 列出所有文档

```bash
python master_ai_importer.py list
```

**输出示例：**
```
============================================================
📚 Lynker Master Vault 文档列表
============================================================

📁 project_docs
------------------------------------------------------------
   - OAUTH_CALLBACK_GUIDE.md
   - UPDATE_REDIRECT_URI_GUIDE.md
   - GDRIVE_MIGRATION_GUIDE.md
   - replit.md

📁 api_docs
------------------------------------------------------------
   - GOOGLE_OAUTH_USAGE.md
   - SUPABASE_SCHEMA_CACHE_FIX.md
   - CHILD_AI_GDRIVE_SYNC.md

📁 dev_brainstorm
------------------------------------------------------------
   - CHILD_AI_MEMORY_SETUP.md
============================================================
```

### 3. 搜索文档

```bash
python master_ai_importer.py search <关键词>

# 示例
python master_ai_importer.py search oauth
```

---

## 🌐 Context API

### 启动 API 服务器

```bash
python master_ai_context_api.py
```

服务器将在 `http://0.0.0.0:8080` 上运行。

### API 端点

#### 1. 健康检查

```bash
GET /api/master-ai/health
```

**响应：**
```json
{
  "status": "healthy",
  "vault_path": "lynker_master_vault",
  "index_exists": true
}
```

#### 2. 获取类别统计

```bash
GET /api/master-ai/categories
```

**响应：**
```json
{
  "project_docs": 4,
  "api_docs": 3,
  "dev_brainstorm": 1,
  "memory": 0
}
```

#### 3. 获取知识摘要

```bash
GET /api/master-ai/context?category=api_docs&max_length=500
```

**参数：**
- `category` (可选) - 筛选类别
- `max_length` (可选) - 摘要最大长度（默认 500）

**响应：**
```json
{
  "total": 3,
  "summaries": [
    {
      "file": "GOOGLE_OAUTH_USAGE.md",
      "category": "api_docs",
      "snippet": "# Google OAuth 2.0 使用手册...",
      "size": 15234,
      "path": "lynker_master_vault/api_docs/GOOGLE_OAUTH_USAGE.md"
    }
  ]
}
```

#### 4. 搜索文档

```bash
GET /api/master-ai/search?q=oauth
```

**响应：**
```json
{
  "query": "oauth",
  "total": 6,
  "results": [
    {
      "file": "OAUTH_CALLBACK_GUIDE.md",
      "category": "project_docs",
      "match_type": "filename"
    },
    {
      "file": "GOOGLE_OAUTH_USAGE.md",
      "category": "api_docs",
      "match_type": "content",
      "context": "...OAuth 2.0 授权流程..."
    }
  ]
}
```

#### 5. 获取索引

```bash
GET /api/master-ai/index
```

**响应：**
```json
{
  "project_docs": [
    {
      "filename": "OAUTH_CALLBACK_GUIDE.md",
      "imported_at": "1761040991.444229"
    }
  ],
  "api_docs": [...],
  "dev_brainstorm": [...]
}
```

---

## 📊 当前状态

### 已导入文档（8 个）

**项目文档（4）：**
- OAUTH_CALLBACK_GUIDE.md
- UPDATE_REDIRECT_URI_GUIDE.md
- GDRIVE_MIGRATION_GUIDE.md
- replit.md

**API 文档（3）：**
- GOOGLE_OAUTH_USAGE.md
- SUPABASE_SCHEMA_CACHE_FIX.md
- CHILD_AI_GDRIVE_SYNC.md

**开发思路（1）：**
- CHILD_AI_MEMORY_SETUP.md

---

## 🔧 高级用法

### 批量导入

```bash
# 导入所有 .md 文件
for file in *.md; do
  python master_ai_importer.py import "$file"
done
```

### 与前端集成

```javascript
// 获取知识摘要
fetch('/api/master-ai/context?max_length=300')
  .then(res => res.json())
  .then(data => {
    console.log(`共 ${data.total} 个文档`);
    data.summaries.forEach(doc => {
      console.log(`${doc.category}/${doc.file}: ${doc.snippet}`);
    });
  });

// 搜索
fetch('/api/master-ai/search?q=oauth')
  .then(res => res.json())
  .then(data => {
    console.log(`找到 ${data.total} 个结果`);
  });
```

### 自定义分类

编辑 `master_ai_importer.py` 中的 `categorize_doc()` 函数：

```python
def categorize_doc(filename):
    lower = filename.lower()
    
    # 添加自定义规则
    if "custom_keyword" in lower:
        return "custom_category"
    
    # ... 其他规则
```

---

## 🛠️ 维护

### 重建索引

```bash
# 删除现有索引
rm lynker_master_vault/index.yaml

# 重新导入所有文档
for category in project_docs api_docs dev_brainstorm; do
  for file in lynker_master_vault/$category/*; do
    [ -f "$file" ] && python master_ai_importer.py import "$file"
  done
done
```

### 清理未使用的文档

```bash
# 手动删除文件后，重建索引
python master_ai_importer.py list
```

---

## 📚 设计理念

1. **自动分类** - 基于文件名关键词自动识别类别
2. **YAML 索引** - 人类可读、易于编辑的索引格式
3. **RESTful API** - 标准化的 HTTP 接口，便于集成
4. **低耦合** - 独立的模块，不影响现有系统
5. **可扩展** - 支持自定义分类规则和新类别

---

## 🔄 未来功能

- [ ] 自动向量化（Embeddings）
- [ ] 语义搜索（Semantic Search）
- [ ] 文档版本管理
- [ ] 自动摘要生成
- [ ] 知识图谱可视化

---

## 📝 使用场景

### 1. AI 助手上下文注入

```python
import requests

# 获取相关文档上下文
context = requests.get('http://localhost:8080/api/master-ai/search?q=oauth').json()

# 注入到 AI prompt
prompt = f"""
基于以下文档回答问题：
{context['results']}

用户问题：如何实现 OAuth 授权？
"""
```

### 2. 文档中心

```bash
# 启动 API 服务器作为文档中心
python master_ai_context_api.py

# 前端访问 API 展示文档
```

### 3. 知识检索

```bash
# 快速查找相关文档
python master_ai_importer.py search "Google Drive"
```

---

## 🎯 总结

Lynker Master Vault 提供了：

✅ **智能文档管理** - 自动分类、索引  
✅ **快速检索** - 文件名和内容搜索  
✅ **RESTful API** - 标准化接口  
✅ **易于集成** - 可与前端和 AI 助手无缝对接

**开始使用：**
```bash
python master_ai_importer.py import <文件路径>
python master_ai_context_api.py
```

🎉 **享受智能文档管理的便利！**
