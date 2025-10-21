# 🚀 Lynker Master Vault 使用指南

**当前 Replit 域名：** `f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev`

---

## 📥 导入文档到 Vault

### 命令格式

```bash
python master_ai_importer.py import <文件路径>
```

### 使用示例

```bash
# 导入项目愿景文档
python master_ai_importer.py import vision.md

# 导入师徒系统笔记
python master_ai_importer.py import guru_system_notes.txt

# 导入 API 结构文档
python master_ai_importer.py import api_structure.docx
```

### 系统会自动

✅ **自动分类保存**
- 根据文件名关键词识别类别
- `vision.md` → `project_docs`
- `guru_system_notes.txt` → `dev_brainstorm`
- `api_structure.docx` → `api_docs`

✅ **更新 YAML 索引**
- 自动维护 `lynker_master_vault/index.yaml`

✅ **控制台显示确认**

```
✅ 已导入 vision.md → project_docs/vision.md
📚 索引已更新 → lynker_master_vault/index.yaml
```

---

## 📊 查看 Vault 内容

### 方式 1: 命令行查看

```bash
# 列出所有文档
python master_ai_importer.py list

# 搜索文档
python master_ai_importer.py search <关键词>
```

**输出示例：**
```
============================================================
📚 Lynker Master Vault 文档列表
============================================================

📁 project_docs
------------------------------------------------------------
   - vision.md
   - OAUTH_CALLBACK_GUIDE.md
   - UPDATE_REDIRECT_URI_GUIDE.md
   - replit.md

📁 dev_brainstorm
------------------------------------------------------------
   - guru_system_notes.txt
   - CHILD_AI_MEMORY_SETUP.md

📁 api_docs
------------------------------------------------------------
   - api_structure.docx
   - GOOGLE_OAUTH_USAGE.md
   - SUPABASE_SCHEMA_CACHE_FIX.md
============================================================
```

### 方式 2: 通过 RESTful API

#### 1. 启动 Context API 服务器

```bash
python master_ai_context_api.py
```

服务器将在端口 8080 上运行。

#### 2. 访问 API 端点

**获取知识摘要：**
```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev:8080/api/master-ai/context
```

**响应示例：**
```json
{
  "total": 10,
  "summaries": [
    {
      "file": "vision.md",
      "category": "project_docs",
      "snippet": "灵客AI的愿景是...",
      "size": 2456,
      "path": "lynker_master_vault/project_docs/vision.md"
    },
    {
      "file": "guru_system_notes.txt",
      "category": "dev_brainstorm",
      "snippet": "师徒AI的结构包括...",
      "size": 3821,
      "path": "lynker_master_vault/dev_brainstorm/guru_system_notes.txt"
    }
  ]
}
```

---

## 🌐 所有可用的 API 端点

### 基础 URL
```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev:8080
```

### 端点列表

#### 1. 健康检查
```
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
```
GET /api/master-ai/categories
```

**响应：**
```json
{
  "project_docs": 4,
  "api_docs": 3,
  "dev_brainstorm": 2,
  "memory": 0
}
```

#### 3. 获取知识摘要
```
GET /api/master-ai/context?category=api_docs&max_length=500
```

**参数：**
- `category` (可选) - 筛选类别（`project_docs`、`api_docs`、`dev_brainstorm`）
- `max_length` (可选) - 摘要最大长度（默认 500）

#### 4. 搜索文档
```
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
```
GET /api/master-ai/index
```

**响应：**
```json
{
  "project_docs": [
    {
      "filename": "vision.md",
      "imported_at": "1761040991.444229"
    }
  ],
  "api_docs": [...],
  "dev_brainstorm": [...]
}
```

---

## 📂 自动分类规则

文档会根据文件名关键词自动分类到对应目录：

| 关键词 | 分类目录 | 示例 |
|--------|---------|------|
| ui, design, dashboard, client, frontend | `project_docs` | vision.md, dashboard_ui.md |
| api, auth, supabase, drive, oauth, backend | `api_docs` | api_structure.md, oauth_guide.md |
| ai, 命理, 同命, 玄学, 太玄, 铁板, guru | `dev_brainstorm` | guru_system_notes.txt, ai_theory.md |

---

## 🔧 高级用法

### 批量导入文档

```bash
# 导入当前目录所有 .md 文件
for file in *.md; do
  python master_ai_importer.py import "$file"
done

# 导入特定目录的文档
for file in docs/*.txt; do
  python master_ai_importer.py import "$file"
done
```

### 在代码中使用 API

```python
import requests

# 获取所有文档摘要
response = requests.get(
    'https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev:8080/api/master-ai/context',
    params={'max_length': 300}
)

data = response.json()
print(f"共 {data['total']} 个文档")

for doc in data['summaries']:
    print(f"📄 {doc['category']}/{doc['file']}")
    print(f"   {doc['snippet'][:100]}...")
```

### 与 AI 助手集成

```python
import requests

# 搜索相关文档
def get_relevant_context(keyword):
    response = requests.get(
        f'https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev:8080/api/master-ai/search',
        params={'q': keyword}
    )
    return response.json()

# 注入到 AI prompt
context = get_relevant_context('oauth')
prompt = f"""
基于以下项目文档回答问题：

{context['results']}

用户问题：如何实现 OAuth 授权？
"""
```

---

## 📊 当前 Vault 状态

**已索引文档：** 8 个

**分类统计：**
- 📁 `project_docs`: 4 个文档
- 📁 `api_docs`: 3 个文档
- 📁 `dev_brainstorm`: 1 个文档

---

## 🎯 快速测试

### 1. 导入测试文档

```bash
# 创建测试文档
echo "这是测试文档" > test_doc.md

# 导入
python master_ai_importer.py import test_doc.md

# 查看
python master_ai_importer.py list
```

### 2. 测试 API

```bash
# 启动服务器
python master_ai_context_api.py &

# 等待几秒后测试
curl "http://localhost:8080/api/master-ai/health"

# 查看所有文档
curl "http://localhost:8080/api/master-ai/context" | python -m json.tool

# 搜索
curl "http://localhost:8080/api/master-ai/search?q=test"
```

---

## 📚 完整文档

- **lynker_master_vault/README.md** - Vault 完整使用文档
- **MASTER_VAULT_QUICKSTART.md** - 快速开始指南

---

## 🎉 开始使用

```bash
# 1. 导入您的第一个文档
python master_ai_importer.py import vision.md

# 2. 查看已导入的文档
python master_ai_importer.py list

# 3. 启动 API 服务器（可选）
python master_ai_context_api.py

# 4. 在浏览器访问
# https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev:8080/api/master-ai/context
```

**🚀 享受智能文档管理的便利！**
