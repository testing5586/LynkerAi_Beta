# 多格式导入功能扩展指南

## 📦 功能概述

命盘批量导入中心现已支持 **4 种导入格式**：

1. ✅ **JSON** - 文墨天机软件导出格式
2. ✅ **TXT** - 纯文本格式
3. ✅ **DOCX** - Microsoft Word 文档格式
4. ✅ **图片 OCR** - 命盘截图识别

---

## 🎯 新增功能

### 1️⃣ **TXT 文本格式导入**

支持纯文本格式的命盘数据，自动提取关键字段。

#### 文本格式示例

```
姓名: 王小明
性别: 男
出生时间: 1988-12-05 08:30
夫妻宫: 紫微
财帛宫: 天相
化禄: 是
化忌: 否
```

#### 支持的字段标签

| 字段 | 支持的标签 |
|------|-----------|
| 姓名 | `姓名:` `name:` `命主:` |
| 性别 | `性别:` `gender:` `sex:` |
| 出生时间 | `出生时间:` `出生:` `生辰:` `birth_time:` |
| 夫妻宫 | `夫妻宫:` `marriage_palace:` |
| 财帛宫 | `财帛宫:` `wealth_palace:` `money_palace:` |
| 化禄 | `化禄:` `hua_lu:` (值: 是/否/true/false) |
| 化忌 | `化忌:` `hua_ji:` (值: 是/否/true/false) |

#### 时间格式支持

- `YYYY-MM-DD HH:MM` → 自动转换为 `YYYY-MM-DDTHH:MM:00`
- `YYYY-MM-DD HH:MM:SS` → 自动转换为 `YYYY-MM-DDTHH:MM:SS`
- `YYYY/MM/DD HH:MM` → 自动转换为 `YYYY-MM-DDTHH:MM:00`
- `YYYY-MM-DD` → 自动添加默认时间 `T12:00:00`

---

### 2️⃣ **DOCX 文档格式导入**

支持 Microsoft Word (.docx) 文档，自动提取文本并识别字段。

#### 依赖安装

```bash
pip install python-docx
```

#### 支持的内容

- ✅ 段落文本
- ✅ 表格内容
- ✅ 中英文混合
- ❌ 不支持 .doc 旧格式（需要转换为 .docx）

#### 使用流程

1. 上传 .docx 文件
2. 系统自动提取文本
3. 使用 TXT 解析器识别字段
4. 人工确认后写入数据库

---

## 🚀 使用指南

### 访问地址

```
https://f7ebbceb-eb1c-41fc-9cf7-dbfc578e05de-00-3h1iq9ru0v8kp.sisko.replit.dev/import
```

### TXT 文件导入

1. 准备 TXT 文件（UTF-8 编码）
2. 点击"📄 文档导入"卡片
3. 选择文件 → 点击"识别并预览"
4. 检查识别结果（可手动修正）
5. 点击"确认写入数据库"

### DOCX 文件导入

1. 准备 DOCX 文件（确保是 .docx 格式，不是 .doc）
2. 点击"📄 文档导入"卡片
3. 选择文件 → 点击"识别并预览"
4. 检查识别结果（可手动修正）
5. 点击"确认写入数据库"

---

## 📂 文件结构

```
admin_dashboard/
  import_engine/
    ✅ normalize_chart.py          (数据规范化器)
    ✅ import_wenmote_json.py      (JSON 导入)
    ✅ txt_importer.py             (TXT 导入 - 新增)
    ✅ doc_importer.py             (DOCX 导入 - 新增)
    ✅ ocr_importer.py             (OCR 导入)
    ✅ import_api.py               (通用 API - 已扩展)
  templates/
    ✅ import_ui.html              (前端界面 - 已更新)

test_data/
  ✅ sample_wenmote.json           (JSON 测试数据)
  ✅ sample_birthchart.txt         (TXT 测试数据 - 新增)
```

---

## 📊 API 端点

### 新增端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/import/file/preview` | POST | 通用文件预览（TXT/DOCX） |
| `/import/file/confirm` | POST | 通用文件确认写入 |

### 完整端点列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/import` | GET | 导入中心首页 |
| `/import/stats` | GET | 命盘统计 |
| `/import/json` | POST | JSON 导入 |
| `/import/file/preview` | POST | TXT/DOCX 预览 |
| `/import/file/confirm` | POST | TXT/DOCX 确认 |
| `/import/ocr/preview` | POST | OCR 预览 |
| `/import/ocr/confirm` | POST | OCR 确认 |

---

## 🧪 测试验证

### TXT 解析器测试

```bash
cd admin_dashboard
python -c "
from import_engine.txt_importer import process_txt_file

content = '''
姓名: 王小明
性别: 男
出生时间: 1988-12-05 08:30
夫妻宫: 紫微
财帛宫: 天相
化禄: 是
化忌: 否
'''

result = process_txt_file(content)
print(result)
"
```

### 预期输出

```
✅ TXT 解析测试成功
姓名: 王小明
性别: 男
出生时间: 1988-12-05T08:30:00
夫妻宫: 紫微
财帛宫: 天相
化禄: True
化忌: False
```

---

## 🔧 技术实现

### TXT 解析器核心逻辑

```python
def extract_fields_from_text(text):
    """使用正则表达式提取字段"""
    - 支持多种标签格式（中英文）
    - 时间格式自动规范化
    - 化禄/化忌布尔值智能转换
    - 多编码支持（UTF-8, GBK, GB2312）
```

### DOCX 解析器核心逻辑

```python
def extract_text_from_docx(file_bytes):
    """提取 Word 文档中的所有文本"""
    - 段落文本提取
    - 表格内容提取
    - 复用 TXT 解析器进行字段识别
```

### 通用文件上传 API

```python
@bp_import.route("/file/preview", methods=["POST"])
def file_preview():
    """自动识别文件格式并调用相应解析器"""
    - .txt → txt_importer
    - .docx → doc_importer
    - .doc → 提示转换为 .docx
```

---

## ⚠️ 注意事项

### 编码支持

TXT 文件支持以下编码：
1. **UTF-8** （推荐）
2. **GBK**
3. **GB2312**

### 格式限制

- ❌ 不支持 .doc 旧格式
- ❌ 不支持 PDF（使用 OCR 功能）
- ✅ 支持 .txt, .docx

### DOCX 依赖

DOCX 功能需要安装 `python-docx`：

```bash
pip install python-docx
```

如未安装，系统会显示友好提示，不影响其他格式导入。

---

## 🎯 使用场景

### 场景 1：批量文本导入

从记事本或文本编辑器批量复制命盘信息 → 保存为 TXT → 导入

### 场景 2：Word 文档迁移

用户在 Word 中整理了大量命盘数据 → 直接上传 DOCX → 导入

### 场景 3：多格式混合

- JSON：从文墨天机软件导出
- TXT：手动录入的简单数据
- DOCX：整理好的文档资料
- OCR：命盘截图

---

## 📈 性能优化

### 文本编码自动检测

```python
for encoding in ['utf-8', 'gbk', 'gb2312']:
    try:
        text = file_content.decode(encoding)
        break
    except UnicodeDecodeError:
        continue
```

### 时间格式智能转换

自动处理多种时间格式，减少用户输入负担。

### 字段缺失兜底

即使某些字段未识别，也能正常导入，避免数据丢失。

---

## 🚨 常见问题

### Q1: TXT 文件识别不准确怎么办？

**A:** 
1. 确保字段标签格式正确（使用冒号分隔）
2. 检查文件编码是否为 UTF-8
3. 在预览界面手动修正识别错误的字段

### Q2: DOCX 文件导入报错

**A:** 
1. 检查是否安装 `python-docx`
2. 确认文件是 .docx 格式（不是 .doc）
3. 尝试用 Word 重新保存为 .docx

### Q3: 出生时间格式不对

**A:** 
支持以下格式：
- `1988-12-05 08:30` ✅
- `1988/12/05 08:30` ✅
- `1988-12-05` ✅（自动添加 12:00:00）

### Q4: 如何批量导入多个 TXT 文件？

**A:** 
目前前端支持单文件上传，批量导入请使用命令行：

```python
# 待开发：批量导入脚本
python import_engine/import_txt_batch.py --dir /path/to/txt_folder
```

---

## ✅ 功能验收清单

- [x] TXT 文本解析器创建
- [x] DOCX 文档解析器创建
- [x] 通用文件上传 API
- [x] 前端 UI 更新（新增文档导入卡片）
- [x] 时间格式自动转换
- [x] 多编码支持
- [x] 测试验证通过
- [x] 文档编写完成

---

**🎉 多格式导入功能扩展完成，支持 JSON / TXT / DOCX / OCR 四种格式！**
