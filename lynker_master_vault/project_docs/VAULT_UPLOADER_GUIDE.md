# 📤 Master Vault 文件上传器使用指南

**在线文档管理系统 - 拖拽上传，自动分类**

---

## 🌐 访问上传器

### 启动服务器

```bash
python master_ai_context_api.py
```

### 访问 URL

**本地测试：**
```
http://localhost:8080/
```

**Replit 环境：**
```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev:8080/
```

---

## 📋 功能特性

### ✨ 核心功能

- ✅ **拖拽上传** - 直接拖拽文件到上传区域
- ✅ **点击上传** - 点击上传区域选择文件
- ✅ **批量上传** - 支持同时上传多个文件
- ✅ **自动分类** - 根据文件名智能分类
- ✅ **实时统计** - 显示当前 Vault 文档数量
- ✅ **进度反馈** - 上传过程实时显示
- ✅ **美观界面** - 现代化深色主题

### 📁 支持的文件类型

- `.md` - Markdown 文档
- `.txt` - 文本文件
- `.pdf` - PDF 文档
- `.docx` - Word 文档
- `.doc` - 旧版 Word 文档

**文件大小限制：** 16MB

---

## 🎯 使用步骤

### 方式 1: 拖拽上传

1. 打开上传器页面
2. 将文件拖拽到上传区域
3. 点击"🚀 上传并导入"按钮
4. 查看上传结果和分类

### 方式 2: 点击选择

1. 打开上传器页面
2. 点击上传区域
3. 在文件选择器中选择文件
4. 点击"🚀 上传并导入"按钮
5. 查看上传结果和分类

### 方式 3: 批量上传

1. 选择多个文件（Ctrl+点击 或 Shift+点击）
2. 拖拽或点击上传
3. 系统会依次处理每个文件
4. 所有文件处理完成后显示结果

---

## 🔧 自动分类规则

上传的文件会根据文件名自动分类：

| 文件名包含 | 分类目录 | 示例 |
|-----------|---------|------|
| ui, design, dashboard, client | `project_docs` | `ui_design.md` |
| api, auth, supabase, oauth | `api_docs` | `api_guide.md` |
| ai, guru, 命理, 玄学 | `dev_brainstorm` | `ai_theory.txt` |
| 其他 | `project_docs` | `notes.md` |

---

## 📊 界面说明

### 统计卡片

顶部显示三个统计卡片：

```
┌──────────────┬──────────────┬──────────────┐
│ 总文档数     │ API 文档     │ 项目文档     │
│     8        │     3        │     4        │
└──────────────┴──────────────┴──────────────┘
```

### 上传区域

中间的拖拽上传区域：

```
╔════════════════════════════════════════╗
║            📤                          ║
║     点击或拖拽文件到此处                ║
║   支持 .md, .txt, .pdf, .docx          ║
╚════════════════════════════════════════╝
```

### 操作按钮

- **🚀 上传并导入** - 执行上传操作
- **🔄 刷新统计** - 更新文档统计数据

### 输出区域

底部显示上传结果：

```
✅ vision.md
   分类: project_docs
   路径: lynker_master_vault/project_docs/vision.md

✅ api_structure.md
   分类: api_docs
   路径: lynker_master_vault/api_docs/api_structure.md
```

---

## 🌐 API 端点

上传器使用以下 API 端点：

### 1. 上传文件

```
POST /api/master-ai/upload
Content-Type: multipart/form-data

参数：
- file: 文件对象

响应：
{
  "success": true,
  "filename": "vision.md",
  "category": "project_docs",
  "path": "lynker_master_vault/project_docs/vision.md",
  "message": "✅ 已导入 vision.md → project_docs"
}
```

### 2. 获取统计

```
GET /api/master-ai/categories

响应：
{
  "project_docs": 4,
  "api_docs": 3,
  "dev_brainstorm": 1,
  "memory": 0
}
```

---

## 🔧 技术实现

### 前端技术

- **HTML5** - 拖拽 API
- **CSS3** - 现代化样式
- **Vanilla JavaScript** - 无框架依赖
- **Fetch API** - 异步上传

### 后端技术

- **Flask** - Web 框架
- **Werkzeug** - 文件安全处理
- **subprocess** - 调用导入脚本
- **tempfile** - 临时文件管理

### 工作流程

```
用户选择文件
    ↓
前端验证文件类型
    ↓
FormData 上传到服务器
    ↓
后端保存到临时目录
    ↓
调用 master_ai_importer.py
    ↓
自动分类并保存
    ↓
更新 YAML 索引
    ↓
删除临时文件
    ↓
返回结果给前端
```

---

## 🧪 测试示例

### 创建测试文件

```bash
# 创建测试文档
echo "# 项目愿景\n这是灵客AI的愿景文档..." > vision.md
echo "# API 文档\nOAuth 授权流程..." > oauth_api.md
echo "# 师徒系统\nGuru AI 设计..." > guru_notes.txt
```

### 上传测试文件

1. 启动服务器：`python master_ai_context_api.py`
2. 打开浏览器访问上传器
3. 拖拽上述 3 个文件
4. 点击上传
5. 查看结果

**预期结果：**
```
✅ vision.md → project_docs
✅ oauth_api.md → api_docs
✅ guru_notes.txt → dev_brainstorm
```

---

## 🔐 安全特性

### 文件验证

- ✅ 文件类型白名单检查
- ✅ 文件名安全处理（`secure_filename`）
- ✅ 文件大小限制（16MB）
- ✅ 超时保护（30秒）

### 临时文件管理

- ✅ 使用系统临时目录
- ✅ 上传后自动清理
- ✅ 独立的临时文件夹

---

## 🎨 界面定制

### 修改主题颜色

编辑 `master_vault_uploader.html`：

```css
/* 修改主色调 */
button {
  background: #4f46e5;  /* 改为你喜欢的颜色 */
}

/* 修改背景色 */
body {
  background: #0f111a;  /* 改为你喜欢的颜色 */
}
```

### 修改上传大小限制

编辑 `master_ai_context_api.py`：

```python
# 修改文件大小限制（默认 16MB）
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 改为 32MB
```

---

## 🐛 常见问题

### 1. 上传失败

**原因：** 文件类型不支持

**解决：** 确保文件扩展名为 `.md`, `.txt`, `.pdf`, `.docx`

### 2. 统计不更新

**原因：** 需要手动刷新

**解决：** 点击"🔄 刷新统计"按钮

### 3. 页面无法访问

**原因：** 服务器未启动

**解决：** 运行 `python master_ai_context_api.py`

### 4. 分类不正确

**原因：** 文件名不包含关键词

**解决：** 重命名文件包含相关关键词，或手动移动到正确目录

---

## 🚀 进阶用法

### 与命令行结合

```bash
# 批量上传所有 .md 文件
for file in docs/*.md; do
  curl -F "file=@$file" http://localhost:8080/api/master-ai/upload
done
```

### 编程接口调用

```python
import requests

# 上传单个文件
with open('vision.md', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8080/api/master-ai/upload',
        files=files
    )
    print(response.json())

# 批量上传
import os
for filename in os.listdir('docs/'):
    if filename.endswith('.md'):
        with open(f'docs/{filename}', 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'http://localhost:8080/api/master-ai/upload',
                files=files
            )
            print(f"✅ {filename}: {response.json()['category']}")
```

---

## 📚 相关文档

- **VAULT_USAGE_GUIDE.md** - Vault 完整使用指南
- **MASTER_VAULT_QUICKSTART.md** - 快速开始
- **lynker_master_vault/README.md** - Vault 详细文档

---

## 🎉 总结

**Master Vault 文件上传器特点：**

✅ **简单易用** - 拖拽即可上传  
✅ **自动分类** - 智能识别文档类型  
✅ **实时反馈** - 立即显示结果  
✅ **批量处理** - 支持多文件上传  
✅ **安全可靠** - 文件验证和大小限制  
✅ **美观现代** - 深色主题界面

**开始使用：**
```bash
python master_ai_context_api.py
# 访问 http://localhost:8080/
```

🚀 **享受便捷的文档管理体验！**
