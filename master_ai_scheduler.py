"""
Master AI Scheduler - 自动定时学习系统
------------------------------------
功能：
✅ 每 N 天自动运行 Evolution Engine（规律提炼）
✅ 每 N 天自动运行 Reasoner（全量用户推理）
✅ 学习结果自动加密存入 Master Vault
✅ 完整日志记录和错误处理
"""

import schedule
import time
from datetime import datetime
from master_ai_evolution_engine import main as evolve
from master_ai_reasoner import reason_all
from master_vault_engine import insert_vault
from multi_model_dispatcher import load_ai_rules

LOG_PATH = "logs/master_ai_scheduler.log"

def write_log(msg):
    """写入调度器日志"""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {msg}\n")
        print(msg)
    except Exception as e:
        print(f"⚠️ 写入日志失败: {e}")

def run_master_self_training():
    """
    执行 Master AI 自学习流程
    1. Evolution Engine - 提炼命盘规律
    2. Reasoner - 全量用户推理
    3. 结果写入 Master Vault
    """
    try:
        rules = load_ai_rules()
        interval_days = rules.get("TRAINING_INTERVAL_DAYS", 7)
        
        write_log("=" * 60)
        write_log(f"🚀 Master AI 自学习启动 | 训练周期: {interval_days} 天")
        write_log("=" * 60)
        
        write_log("\n📊 阶段 1/3: Evolution Engine - 提炼命盘规律...")
        try:
            evolve()
            write_log("✅ Evolution Engine 完成")
        except Exception as e:
            write_log(f"❌ Evolution Engine 失败: {e}")
            raise
        
        write_log("\n🧠 阶段 2/3: Reasoner - 全量用户推理（前100位）...")
        try:
            reason_all(limit=100)
            write_log("✅ Reasoner 完成")
        except Exception as e:
            write_log(f"❌ Reasoner 失败: {e}")
            raise
        
        write_log("\n🔐 阶段 3/3: 写入 Master Vault...")
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            summary = f"""
Master AI 自学习纪要 - {datetime.now().strftime('%Y年%m月%d日')}

📊 执行时间: {timestamp}
🔄 训练周期: {interval_days} 天

✅ 完成项目:
1. Evolution Engine - 命盘规律自动提炼
2. Reasoner Engine - 全量用户推理（前100位）
3. 高置信度洞察加密存储

🎯 系统状态: 正常
📈 学习效果: 规律库已更新
🔒 安全等级: AES256 加密

下次执行: {interval_days} 天后
            """
            
            insert_vault(
                title=f"Master AI 自学习纪要 - {datetime.now().strftime('%Y-%m-%d')}",
                content=summary.strip(),
                created_by="Master AI Scheduler"
            )
            write_log("✅ Master Vault 写入完成")
        except Exception as e:
            write_log(f"⚠️ Vault 写入失败（非致命错误）: {e}")
        
        write_log("\n" + "=" * 60)
        write_log("🎉 Master AI 自学习完成！")
        write_log("=" * 60 + "\n")
        
    except Exception as e:
        write_log(f"\n❌ 自学习过程出错: {e}")
        write_log("=" * 60 + "\n")
        raise

def start_scheduler():
    """启动定时调度器"""
    try:
        rules = load_ai_rules()
        interval_days = rules.get("TRAINING_INTERVAL_DAYS", 7)
        
        write_log(f"\n🧠 Master AI Scheduler 启动")
        write_log(f"⏰ 调度周期: 每 {interval_days} 天")
        write_log(f"📝 日志路径: {LOG_PATH}")
        write_log(f"🚀 首次运行: 立即执行")
        write_log("-" * 60 + "\n")
        
        schedule.every(interval_days).days.do(run_master_self_training)
        
        write_log("⏳ 执行首次自学习...")
        run_master_self_training()
        
        write_log(f"\n✅ 调度器就绪，下次执行: {interval_days} 天后")
        write_log("💤 进入等待模式（每小时检查一次）...\n")
        
        while True:
            schedule.run_pending()
            time.sleep(3600)
            
    except KeyboardInterrupt:
        write_log("\n🛑 调度器被手动停止")
    except Exception as e:
        write_log(f"\n❌ 调度器启动失败: {e}")
        raise

if __name__ == "__main__":
    start_scheduler()
