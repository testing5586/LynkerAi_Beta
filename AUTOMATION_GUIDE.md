# LynkerAI 自动化运行指南
# LynkerAI Automation Guide

## 🚀 快速开始 (Quick Start)

### 方法 1: 双击启动 (Double-Click to Start)
最简单的方法 - 直接双击桌面上的 `Start LynkerAI.bat` 文件

The easiest method - simply double-click the `Start LynkerAI.bat` file

### 方法 2: 命令行启动 (Command Line Start)
```bash
python auto_start_lynkerai.py
```

## 🔧 完全自动化设置 (Full Automation Setup)

### 开机自动启动 (Start with Windows)
运行以下命令设置开机自动启动：
Run the following command to set up automatic startup with Windows:

```bash
python setup_autostart.py
```

这将：
- This will:
  - 添加 LynkerAI 到 Windows 启动项
  - Add LynkerAI to Windows startup
  - 每次开机自动运行
  - Automatically run every time you start Windows
  - 在后台静默启动
  - Start silently in the background

## 📋 自动化功能说明 (Automation Features)

### 自动数据库初始化 (Automatic Database Initialization)
- 自动检测 Supabase 连接
- Automatically detect Supabase connection
- 自动创建缺失的表和函数
- Automatically create missing tables and functions
- 自动验证数据库设置
- Automatically verify database setup

### 自动浏览器打开 (Automatic Browser Launch)
- 启动后自动打开浏览器
- Automatically open browser after startup
- 自动导航到登录页面
- Automatically navigate to login page
- 显示登录密码
- Display login password

### 自动错误处理 (Automatic Error Handling)
- 数据库连接失败时继续运行
- Continue running if database connection fails
- 自动重试机制
- Automatic retry mechanism
- 详细的错误日志
- Detailed error logging

## 🛠️ 自定义配置 (Customization)

### 修改启动参数 (Modify Startup Parameters)
编辑 `auto_start_lynkerai.py` 可以自定义：
Edit `auto_start_lynkerai.py` to customize:

```python
# 修改等待时间 (Modify wait time)
time.sleep(3)  # 改为 5 等待更长时间

# 修改启动端口 (Modify startup port)
url = "http://localhost:5000/admin"  # 改为其他端口

# 禁用自动打开浏览器 (Disable auto browser launch)
# webbrowser.open(url)  # 注释掉这行
```

### 修改登录密码 (Modify Login Password)
编辑 `.env` 文件中的 `MASTER_VAULT_KEY`：
Edit `MASTER_VAULT_KEY` in `.env` file:

```env
MASTER_VAULT_KEY=your_custom_32_character_key
```

## 🔍 故障排除 (Troubleshooting)

### 问题 1: 应用无法启动 (App Won't Start)
**解决方案 (Solution):**
1. 检查 Python 是否正确安装
   Check if Python is properly installed
2. 运行 `pip install -r requirements.txt`
3. 确保 `.env` 文件存在且配置正确
   Ensure `.env` file exists and is configured correctly

### 问题 2: 数据库连接失败 (Database Connection Failed)
**解决方案 (Solution):**
1. 检查 `.env` 文件中的 Supabase 凭据
   Check Supabase credentials in `.env` file
2. 手动运行 `python auto_setup_supabase.py`
   Manually run `python auto_setup_supabase.py`
3. 检查网络连接
   Check network connection

### 问题 3: 浏览器未自动打开 (Browser Not Opening)
**解决方案 (Solution):**
1. 手动访问 http://localhost:5000/admin
   Manually visit http://localhost:5000/admin
2. 检查默认浏览器设置
   Check default browser settings
3. 防火墙可能阻止了自动打开
   Firewall might be blocking auto-launch

## 📝 日志文件 (Log Files)

应用运行时会产生以下日志文件：
The following log files are generated during operation:

- `master_log.json` - 主应用日志
- `ai_usage_log.jsonl` - AI 使用日志
- `conversation_log.jsonl` - 聊天记录
- `memory_sync_state.json` - 内存同步状态

## 🔄 更新和维护 (Updates and Maintenance)

### 更新应用 (Update Application)
1. 下载新版本到同一目录
   Download new version to same directory
2. 自动化脚本会继续工作
   Automation scripts will continue to work
3. 重新运行 `python setup_autostart.py` 如果需要
   Re-run `python setup_autostart.py` if needed

### 备份配置 (Backup Configuration)
重要文件备份：
Important files to backup:

- `.env` - 环境配置
- `auto_start_lynkerai.py` - 自动启动脚本
- `Start LynkerAI.bat` - 启动批处理文件

## 📞 获取帮助 (Getting Help)

如果遇到问题：
If you encounter issues:

1. 检查终端输出的错误信息
   Check error messages in terminal
2. 查看日志文件
   Check log files
3. 确保所有依赖都已安装
   Ensure all dependencies are installed
4. 重新运行自动化设置
   Re-run automation setup

---

**注意 (Note):** 自动化脚本设计为在后台运行，不会干扰您的正常工作。
**Note:** Automation scripts are designed to run in the background without interfering with your normal work.