# 🚀 Lynker Master Vault 快速开始

**一分钟上手 AI 知识仓库！**

---

## ⚡ 快速命令

```bash
# 1️⃣ 导入文档
python master_ai_importer.py import <文件路径>

# 2️⃣ 查看所有文档
python master_ai_importer.py list

# 3️⃣ 搜索文档
python master_ai_importer.py search <关键词>

# 4️⃣ 启动 API 服务器
python master_ai_context_api.py
```

---

## 📊 当前状态

### 已导入 8 个文档

**📁 项目文档（4）：**
- OAUTH_CALLBACK_GUIDE.md
- UPDATE_REDIRECT_URI_GUIDE.md
- GDRIVE_MIGRATION_GUIDE.md
- replit.md

**📁 API 文档（3）：**
- GOOGLE_OAUTH_USAGE.md
- SUPABASE_SCHEMA_CACHE_FIX.md
- CHILD_AI_GDRIVE_SYNC.md

**📁 开发思路（1）：**
- CHILD_AI_MEMORY_SETUP.md

---

## 🌐 API 端点

```bash
# 健康检查
GET http://localhost:8080/api/master-ai/health

# 获取类别统计
GET http://localhost:8080/api/master-ai/categories

# 搜索文档
GET http://localhost:8080/api/master-ai/search?q=oauth

# 获取知识摘要
GET http://localhost:8080/api/master-ai/context?max_length=500

# 获取索引
GET http://localhost:8080/api/master-ai/index
```

---

## 🎯 使用示例

### 导入新文档

```bash
python master_ai_importer.py import NEW_DOC.md
# ✅ 已导入 NEW_DOC.md → api_docs/NEW_DOC.md
# 📚 索引已更新 → lynker_master_vault/index.yaml
```

### 搜索 OAuth 相关文档

```bash
python master_ai_importer.py search oauth
# 🔍 搜索结果 (关键词: oauth)
# ============================================================
#    project_docs/OAUTH_CALLBACK_GUIDE.md
#    api_docs/GOOGLE_OAUTH_USAGE.md
#    ...
```

### 调用 API

```bash
# 启动服务器
python master_ai_context_api.py &

# 调用 API
curl http://localhost:8080/api/master-ai/categories
# {"api_docs": 3, "dev_brainstorm": 1, "project_docs": 4, "memory": 0}
```

---

## 🔧 自动分类规则

文档会根据文件名自动分类：

| 关键词 | 分类 |
|-------|------|
| ui, design, dashboard, client | **project_docs** |
| api, auth, supabase, oauth | **api_docs** |
| ai, 命理, 同命, 玄学 | **dev_brainstorm** |

---

## 📚 完整文档

详见 `lynker_master_vault/README.md`

---

## ✅ 测试结果

```
🧪 测试 Master AI Context API...
============================================================
✅ Health: {'status': 'healthy', 'vault_path': 'lynker_master_vault', 'index_exists': True}
✅ Categories: {'project_docs': 4, 'api_docs': 3, 'dev_brainstorm': 1, 'memory': 0}
✅ Search results: Found 6 documents
✅ Context: 8 documents indexed
============================================================
🎉 所有测试通过！
```

---

## 🎉 开始使用

```bash
# 导入您的第一个文档
python master_ai_importer.py import YOUR_DOC.md

# 查看所有文档
python master_ai_importer.py list

# 启动 API 服务器
python master_ai_context_api.py
```

**🚀 享受智能文档管理的便利！**
