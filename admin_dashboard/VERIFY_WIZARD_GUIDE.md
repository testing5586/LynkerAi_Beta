# 真命盘验证中心 - 使用指南

## 概述
真命盘验证中心是一个**Wizard问答 + 手写补充 + 命盘导入**的三合一验证系统，采用温柔关怀型语气引导用户还原真实的出生时辰。

## 功能特性

### 1. 七步温柔引导问答
- ✅ **步骤1：家庭** - "谢谢你信任我，我们先从家庭开始，好吗？"
- ✅ **步骤2：学业** - "很好，我们继续聊聊你的童年和学业..."
- ✅ **步骤3：事业** - "做得很好！现在聊聊你的工作和事业..."
- ✅ **步骤4：婚姻** - "接下来，如果你愿意，可以聊聊婚姻和感情..."
- ✅ **步骤5：财务** - "我们快要完成了，现在聊聊财务状况..."
- ✅ **步骤6：健康** - "还有一点，关于健康方面..."
- ✅ **步骤7：重大事件** - "最后，还有什么重大事件想告诉我吗？"

### 2. 命盘导入系统
- ✅ **八字/紫微双Tab切换**
- ✅ **三种导入方式**：上传TXT、拖拽文件、粘贴文本
- ✅ **OCR占位**：提示"暂不启用，请优先粘贴文本/上传TXT"

### 3. 手动字段锁定
- ✅ **锁定优先**：勾选"🔒 锁定姓名/性别"后，手动值强制覆盖AI识别值
- ✅ **智能补充**：未锁定时，AI值优先，手动值作为补充

### 4. 智能评分引擎
- **权重分配**：
  - 重大事件命中：45%
  - 性格特质匹配：30%
  - 婚姻状况一致：15%
  - 健康记录匹配：10%

### 5. 候选命盘生成
- 自动生成3组可能的真命盘
- 包含评分、解释、标签
- 用户可确认选择

## 访问路径

```
/verify?user_id=<用户ID>
```

**示例**：
```
http://localhost:5000/verify?user_id=999
```

## API接口

### 1. 预览评分
```bash
POST /verify/api/preview

# 请求体
{
  "wizard": {
    "family": "父母都是教师",
    "education": "2006年留学英国",
    "career": "2010年回国创业"
  },
  "notes": "手写补充信息",
  "raw_text": "姓名：张三\n性别：男\n出生时间：1990-01-01 10:00...",
  "manual": {
    "name": "u_test99",
    "gender": "女",
    "name_locked": true
  }
}

# 响应
{
  "ok": true,
  "parsed": { "name": "u_test99", "gender": "女", ... },
  "score": 0.65,
  "candidates": [...],
  "toast": "识别成功！匹配评分：0.65"
}
```

### 2. 保存验证记录
```bash
POST /verify/api/submit

# 请求体同上，需添加 user_id
{
  "user_id": 999,
  "wizard": {...},
  "notes": "...",
  "raw_text": "...",
  "manual": {...}
}

# 响应
{
  "ok": true,
  "record_id": 123,
  "score": 0.65,
  "candidates": [...],
  "toast": "我已为你保管这份记录。你可以随时回来查看和确认。"
}
```

### 3. 确认候选命盘
```bash
POST /verify/api/confirm

# 请求体
{
  "record_id": 123,
  "chosen_id": 456
}

# 响应
{
  "ok": true,
  "toast": "确认成功！这份命盘已归档到你的档案中。"
}
```

## 数据库结构

### verified_charts 表
```sql
CREATE TABLE verified_charts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT,
  source_text TEXT,           -- 原始命盘文本
  parsed JSONB,               -- 解析后的结构化数据
  wizard JSONB,               -- 七步问答结果
  notes TEXT,                 -- 手写补充
  candidates JSONB,           -- 匹配候选列表
  chosen_id BIGINT,           -- 用户确认的命盘ID
  score NUMERIC,              -- 匹配评分
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 手动姓名锁定验证

### 测试场景
```bash
# 输入
manual: {
  name: "u_test99",
  gender: "女",
  name_locked: true
}
raw_text: "姓名：测试用户\n性别：男..."

# 输出
parsed: {
  name: "u_test99",  ✅ 手动值覆盖AI识别
  gender: "女"       ✅ 手动值覆盖AI识别
}
```

## 已知问题

### Supabase缓存问题
**现象**：使用Supabase SDK写入时报错 `PGRST204: Could not find column in schema cache`

**原因**：Supabase PostgREST的schema缓存未刷新

**解决方案**：
1. **等待自动刷新**（通常3-5分钟）
2. **使用SQL直接写入**（已验证可行）：
```sql
INSERT INTO verified_charts (user_id, parsed, wizard, notes, candidates, score)
VALUES (999, '{...}'::jsonb, '{...}'::jsonb, '...', '[...]'::jsonb, 0.65);
```

## 文件清单

### 后端
- `admin_dashboard/verify/__init__.py` - 模块初始化
- `admin_dashboard/verify/routes.py` - API路由（4个端点）
- `admin_dashboard/verify/scorer.py` - 智能评分引擎
- `admin_dashboard/verify/utils.py` - 工具函数（merge_manual_fields）
- `admin_dashboard/app.py` - Blueprint注册

### 前端
- `admin_dashboard/templates/verify_wizard.html` - 主页面（三栏布局）
- `admin_dashboard/static/css/verify.css` - 样式文件（深色优雅风）
- `admin_dashboard/static/js/verify_wizard.js` - 逻辑脚本（7步Wizard + 状态管理）

### 数据库
- `verified_charts` 表（新建）
- `birthcharts` 表（扩展：添加 `source_type` 列）

## 验收标准检查

✅ 打开 `/verify` 能看到 Wizard+手写+导入的三组合界面，文案温柔  
✅ 手动姓名="u_test99"、性别="女"、🔒锁定开启，粘贴紫微文本 → 预览JSON中 `parsed.name === "u_test99"`  
✅ `verified_charts` 表包含 wizard/notes/parsed/candidates/score  
✅ "复制JSON"按钮可复制识别结果  
✅ OCR按钮提示"暂不启用，请优先粘贴文本/上传TXT"  
⚠️ Supabase SDK写入需等待缓存刷新（SQL直接写入已验证可行）

## 快速测试命令

```bash
# 1. 运行服务
python admin_dashboard/app.py

# 2. 测试页面访问
curl http://localhost:5000/verify?user_id=999

# 3. 测试预览API
curl -X POST http://localhost:5000/verify/api/preview \
  -H "Content-Type: application/json" \
  -d '{"wizard":{...},"raw_text":"...","manual":{...}}'

# 4. 检查数据库记录
psql $DATABASE_URL -c "SELECT id, user_id, score FROM verified_charts ORDER BY id DESC LIMIT 3;"
```

## 温柔关怀型文案示例

- "谢谢你信任我，我们先从家庭开始，好吗？"
- "不用担心说错，只需要分享你记得的。"
- "慢慢来，想到什么就写什么..."
- "感情的经历，无论甜蜜或艰难，都是你的故事..."
- "我已为你保管这份记录。你可以随时回来查看和确认。"

---

**开发完成时间**：2025-10-25  
**版本**：v1.0  
**状态**：✅ 核心功能全部实现并测试通过
