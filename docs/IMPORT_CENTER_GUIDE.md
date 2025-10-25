# 命盘批量导入中心使用指南

## 📦 系统概述

命盘批量导入中心为 LynkerAI 提供多源命盘数据导入能力，支持文墨天机 JSON 和图片 OCR 两种导入方式。

---

## 🌟 核心功能

### 1️⃣ 文墨天机 JSON 导入
- ✅ 自动解析文墨天机软件导出的 JSON 格式
- ✅ 提取姓名、性别、出生时间
- ✅ 识别夫妻宫、财帛宫主星
- ✅ 解析飞化信息（化禄/化忌）
- ✅ 一键上传写入 Supabase

### 2️⃣ 图片 OCR 半自动导入
- ✅ 使用 EasyOCR 识别命盘截图
- ✅ 支持中文 + 英文混合识别
- ✅ 提供可编辑预览界面
- ✅ 人工确认后写入数据库

---

## 🚀 快速开始

### 访问导入中心

```
http://localhost:5000/admin/import
```

### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/admin/import` | GET | 导入中心首页 |
| `/admin/import/json` | POST | 上传文墨 JSON |
| `/admin/import/ocr/preview` | POST | OCR 图片预览 |
| `/admin/import/ocr/confirm` | POST | 确认 OCR 结果 |

---

## 📋 文墨 JSON 导入

### 期望 JSON 格式

```json
{
  "name": "张三",
  "gender": "男",
  "birth_time": "1990-05-20T14:30:00",
  "palaces": {
    "夫妻宫": {"main_star": "天府"},
    "财帛宫": {"main_star": "武曲"}
  },
  "transformations": {
    "hualu": true,
    "huaji": false
  }
}
```

### 使用步骤

1. 从文墨天机软件导出命盘为 JSON 格式
2. 点击"选择文件"上传 JSON
3. 点击"上传并导入"
4. 看到 "✅ 导入成功" 提示

### 批量导入（命令行）

```bash
cd admin_dashboard
python import_engine/import_wenmote_json.py --dir /path/to/json_folder
```

---

## 🖼️ OCR 图片导入

### 依赖安装

OCR 功能需要额外依赖：

```bash
pip install pillow easyocr
```

⚠️ **首次使用会下载 100MB+ 模型文件**，请耐心等待

### 使用步骤

1. **上传图片** - 点击"选择文件"选择命盘截图
2. **OCR 识别** - 点击"识别并预览"
3. **检查字段** - 在左侧文本框中检查识别结果
4. **手动修正** - 修正识别错误的字段
5. **确认写入** - 点击"确认写入数据库"

### 识别字段说明

OCR 会尝试识别以下字段：

| 字段 | 识别规则 |
|------|----------|
| 姓名 | `姓名:` 或 `name:` 后的文本 |
| 性别 | `性别:` 或 `gender:` 后的 `男`/`女` |
| 出生时间 | `出生:` 或 `birth:` 后的时间字符串 |
| 夫妻宫 | `夫妻宫:` 后的主星名称 |
| 财帛宫 | `财帛宫:` 后的主星名称 |
| 化禄 | 识别到 `化禄` 或 `HuaLu` 关键词 |
| 化忌 | 识别到 `化忌` 或 `HuaJi` 关键词 |

### 可编辑预览格式

```json
{
  "name": "命主",
  "gender": "女",
  "birth_time": "1995-03-15T10:20:00",
  "marriage_palace_star": "贪狼",
  "wealth_palace_star": "天机",
  "transformations": {
    "hualu": false,
    "huaji": true
  }
}
```

---

## 🔧 数据规范化

所有导入的数据会经过规范化处理，统一成标准 `birth_data` 结构：

```python
{
    "marriage_palace_star": "天府",
    "wealth_palace_star": "武曲",
    "transformations": {
        "hualu": True,
        "huaji": False
    }
}
```

存入 Supabase 的记录格式：

```python
{
    "name": "张三",
    "gender": "男",
    "birth_time": "1990-05-20T14:30:00",
    "ziwei_palace": None,
    "main_star": None,
    "shen_palace": None,
    "birth_data": {
        "marriage_palace_star": "天府",
        "wealth_palace_star": "武曲",
        "transformations": {"hualu": True, "huaji": False}
    }
}
```

---

## 📂 文件结构

```
admin_dashboard/
  import_engine/
    __init__.py
    normalize_chart.py          # 数据规范化器
    import_wenmote_json.py      # 文墨 JSON 导入器
    ocr_importer.py             # OCR 识别引擎
    import_api.py               # Flask API 路由
    test_import.py              # 测试脚本
  templates/
    import_ui.html              # 导入中心前端
```

---

## 🧪 测试验证

运行测试脚本：

```bash
cd admin_dashboard
python import_engine/test_import.py
```

测试包含：
- ✅ 文墨 JSON 规范化测试
- ✅ OCR 数据规范化测试
- ✅ 字段正确性验证

---

## 🔐 环境变量

系统使用以下环境变量（已配置）：

- `SUPABASE_URL` - Supabase 项目 URL
- `SUPABASE_KEY` - Supabase 服务密钥

---

## ⚠️ 注意事项

### OCR 识别准确度

- OCR 识别准确度受图片质量影响
- **务必在"可编辑预览"界面检查字段**
- 修正错误后再点击"确认写入"

### 文墨 JSON 兼容性

- 支持多种文墨天机导出格式
- 使用兜底逻辑处理不同键名：
  - 夫妻宫: `夫妻宫` / `Spouse` / `marriage`
  - 财帛宫: `财帛宫` / `Wealth` / `money`

### 数据库写入

- 所有导入操作直接写入 `birthcharts` 表
- 失败时返回错误信息，不影响现有数据
- 建议先测试单条导入，确认无误后批量导入

---

## 🎯 使用场景

### 场景 1：历史数据迁移
从文墨天机软件导出所有命盘 → 批量 JSON 导入

```bash
python import_engine/import_wenmote_json.py --dir ~/Downloads/wenmote_charts
```

### 场景 2：快速录入新命盘
用户发送命盘截图 → OCR 识别 → 人工确认 → 写入

### 场景 3：数据校验与补全
导入基础数据后，通过 AI Verifier 进行语义验证

---

## 📊 导入统计

导入中心首页会显示当前数据库统计：
- 总命盘记录数
- （可扩展）今日导入数
- （可扩展）本周导入数

---

## 🚨 常见问题

### Q1: OCR 识别失败怎么办？
**A:** 检查是否安装依赖：
```bash
pip list | grep easyocr
```
如未安装：
```bash
pip install pillow easyocr
```

### Q2: JSON 导入报错 "JSON 格式错误"
**A:** 检查 JSON 文件编码是否为 UTF-8，确保没有语法错误

### Q3: 识别的时间格式不对
**A:** 在可编辑预览中修正为标准格式：`YYYY-MM-DDTHH:MM:SS`
例如：`1990-05-20T14:30:00`

### Q4: 如何扩展识别规则？
**A:** 编辑 `ocr_importer.py` 中的正则表达式规则，添加新的关键词匹配

---

## ✅ 验收清单

- [x] 导入中心页面可访问 (`/admin/import`)
- [x] 文墨 JSON 导入功能正常
- [x] OCR 预览功能可用
- [x] 数据规范化正确
- [x] 写入 Supabase 成功
- [x] 测试脚本通过

---

**🎉 命盘批量导入中心部署完成，可立即投入使用！**
