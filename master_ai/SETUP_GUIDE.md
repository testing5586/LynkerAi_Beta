# LynkerAI TMS v1.0 快速设置指南

## 🎯 5分钟快速启动

### 步骤 1: 配置安全密钥（重要！）

在 Replit Secrets 中添加：
\`\`\`
TMS_SECRET_KEY=your_random_secret_key_at_least_32_chars
\`\`\`

**生成安全密钥示例：**
\`\`\`bash
python3 -c "import secrets; print(secrets.token_hex(32))"
\`\`\`

### 步骤 2: 数据库已就绪 ✅

数据库表已自动创建，包括：
- ✅ \`user_profiles\` - 假名制用户档案
- ✅ \`tms_verified_charts\` - 已验证命盘
- ✅ \`verification_logs\` - 验证记录
- ✅ \`confidence_votes\` - 置信投票
- ✅ \`regional_configs\` - 区域配置
- ✅ \`ai_nodes\` - AI节点注册

### 步骤 3: 启动验证器

\`\`\`bash
cd master_ai
python master_validator.py
\`\`\`

### 步骤 4: 测试系统

打开新终端并运行：
\`\`\`bash
cd master_ai
python demo_tms.py
\`\`\`

您将看到完整的演示流程：
1. 签章生成
2. 签章验证
3. 伪造签章拒绝
4. 多AI协作验证

## 📚 完整文档

查看 \`README_TMS_v1.md\` 了解：
- API端点详情
- 数据库架构
- 安全机制
- 区域适配
- 扩展性方案

## 🔧 故障排查

**问题：** 端口8080已被占用  
**解决：** 修改 \`master_validator.py\` 中的端口号

**问题：** 数据库连接失败  
**解决：** 检查 \`DATABASE_URL\` 环境变量

**问题：** 签章验证失败  
**解决：** 确保 \`TMS_SECRET_KEY\` 在所有节点上一致

## 🚀 下一步

1. 集成到现有系统（参考README示例代码）
2. 配置区域适配（添加更多区域）
3. 实现Child AI节点自动注册
4. 设置置信投票阈值

---

**祝您使用愉快！** 🌟
