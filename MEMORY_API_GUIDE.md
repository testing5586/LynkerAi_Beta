# Master AI Memory API 使用指南

## 概述
Memory API 提供 RESTful 接口访问已同步的子AI记忆数据，支持查询、过滤和搜索功能。

## 服务信息
- **端口**: 9000
- **基础 URL**: `http://localhost:9000`

## API 端点

### 1. 获取记忆数据
**端点**: `GET /api/master-ai/memory`

**查询参数**:
- `user_id` (可选): 按用户ID过滤
- `tag` (可选): 按标签过滤 (例如: `vault`, `project_docs`)
- `limit` (可选): 返回条数限制，默认20

**返回格式**:
```json
{
  "status": "ok",
  "count": 5,
  "memories": [
    {
      "id": 18,
      "user_id": "web_upload",
      "partner_id": "doc_example.md",
      "summary": "文档摘要内容...",
      "tags": ["vault", "project_docs"],
      "similarity": 0.95,
      "interaction_count": 1,
      "last_interaction": "2025-10-21T12:19:04",
      "created_at": "2025-10-21T12:19:04"
    }
  ]
}
```

**示例**:
```python
import requests

# 获取所有记忆（最多10条）
response = requests.get('http://localhost:9000/api/master-ai/memory', 
                       params={'limit': 10})
data = response.json()

# 按标签过滤
response = requests.get('http://localhost:9000/api/master-ai/memory',
                       params={'tag': 'vault', 'limit': 5})

# 按用户ID过滤
response = requests.get('http://localhost:9000/api/master-ai/memory',
                       params={'user_id': 'web_upload', 'limit': 20})
```

### 2. 模糊搜索记忆
**端点**: `GET /api/master-ai/memory/search`

**查询参数**:
- `q` (必需): 搜索关键词
- `limit` (可选): 返回条数限制，默认20

**返回格式**:
```json
{
  "status": "ok",
  "count": 3,
  "results": [
    {
      "id": 15,
      "summary": "包含搜索关键词的记忆摘要...",
      "tags": ["vault"],
      "last_interaction": "2025-10-21T12:00:00"
    }
  ]
}
```

**示例**:
```python
import requests

# 搜索包含"文档"的记忆
response = requests.get('http://localhost:9000/api/master-ai/memory/search',
                       params={'q': '文档', 'limit': 5})
data = response.json()
print(f'找到 {data["count"]} 条相关记忆')
```

### 3. 健康检查
**端点**: `GET /`

**返回**: HTML 页面显示 "✅ Master AI Memory API running"

## 使用场景

### 场景1: 聊天接口调用
```python
# Master AI 回答问题时查询相关记忆
def get_context_for_question(question):
    response = requests.get(
        'http://localhost:9000/api/master-ai/memory/search',
        params={'q': question, 'limit': 5}
    )
    return response.json()['results']

# 使用示例
context = get_context_for_question("最近上传了哪些研究文档?")
```

### 场景2: 后台分析记忆增长趋势
```python
# 获取最近的记忆活动
response = requests.get(
    'http://localhost:9000/api/master-ai/memory',
    params={'limit': 100}
)
memories = response.json()['memories']

# 分析标签分布
from collections import Counter
tag_counts = Counter()
for mem in memories:
    tag_counts.update(mem['tags'])

print("标签分布:", dict(tag_counts))
```

### 场景3: 日志与语义索引的交叉验证
```python
# 检查特定文档是否成功同步
import requests

doc_name = "project_overview.md"
response = requests.get(
    'http://localhost:9000/api/master-ai/memory/search',
    params={'q': doc_name, 'limit': 1}
)
results = response.json()['results']
if results:
    print(f"✅ 文档 {doc_name} 已同步到子AI记忆")
else:
    print(f"⚠️ 文档 {doc_name} 未找到")
```

## 错误处理

### 错误响应格式
```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

### 常见错误
- **400**: 缺少必需参数 (例如搜索时未提供 `q` 参数)
- **500**: 服务器错误 (Supabase 连接失败等)

## 技术说明

### 数据源
- 所有数据来自 Supabase `child_ai_memory` 表
- 自动同步自 Upload API 的上传日志

### 性能优化
- 默认按 `last_interaction` 降序排序
- 建议使用 `limit` 参数控制返回数据量
- 搜索使用 PostgreSQL ILIKE，支持模糊匹配

### 中文支持
- 完全支持中文关键词搜索
- 确保请求使用 UTF-8 编码

## 相关文档
- [Upload API 指南](VAULT_UPLOADER_GUIDE.md)
- [Memory Bridge 说明](master_ai_memory_bridge.py)
