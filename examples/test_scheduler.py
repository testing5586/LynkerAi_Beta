"""
Master AI Scheduler 测试脚本
测试调度器组件是否正常工作（不执行完整流程）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_model_dispatcher import load_ai_rules
from datetime import datetime

LOG_PATH = "logs/master_ai_scheduler.log"

def test_config_loading():
    """测试 1: 配置加载"""
    print("=== 测试 1: AI 规则配置加载 ===")
    try:
        rules = load_ai_rules()
        interval = rules.get("TRAINING_INTERVAL_DAYS", 7)
        print(f"✅ 训练周期: {interval} 天")
        print(f"   MODEL_FREE: {rules.get('MODEL_FREE')}")
        print(f"   MODEL_PRO: {rules.get('MODEL_PRO')}")
        print(f"   MODEL_MASTER: {rules.get('MODEL_MASTER')}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False

def test_log_writing():
    """测试 2: 日志写入"""
    print("\n=== 测试 2: 日志系统 ===")
    try:
        os.makedirs("logs", exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] 🧪 测试日志写入\n")
        print(f"✅ 日志路径: {LOG_PATH}")
        print(f"   最近日志:")
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-3:]:
                print(f"   {line.strip()}")
        return True
    except Exception as e:
        print(f"❌ 日志写入失败: {e}")
        return False

def test_module_imports():
    """测试 3: 模块导入"""
    print("\n=== 测试 3: 模块导入 ===")
    try:
        from master_ai_evolution_engine import main as evolve
        print("✅ master_ai_evolution_engine 导入成功")
        
        from master_ai_reasoner import reason_all
        print("✅ master_ai_reasoner 导入成功")
        
        from master_vault_engine import insert_vault
        print("✅ master_vault_engine 导入成功")
        
        import schedule
        print("✅ schedule 库导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_scheduler_setup():
    """测试 4: 调度器设置"""
    print("\n=== 测试 4: 调度器设置 ===")
    try:
        import schedule
        rules = load_ai_rules()
        interval = rules.get("TRAINING_INTERVAL_DAYS", 7)
        
        def dummy_task():
            print("🧪 测试任务执行")
        
        schedule.every(interval).days.do(dummy_task)
        print(f"✅ 调度器配置成功: 每 {interval} 天执行一次")
        print(f"   当前待执行任务数: {len(schedule.jobs)}")
        
        schedule.clear()
        return True
    except Exception as e:
        print(f"❌ 调度器设置失败: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Master AI Scheduler 系统测试")
    print("=" * 60 + "\n")
    
    results = []
    results.append(("配置加载", test_config_loading()))
    results.append(("日志系统", test_log_writing()))
    results.append(("模块导入", test_module_imports()))
    results.append(("调度器设置", test_scheduler_setup()))
    
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！调度器系统就绪。")
        print("\n📝 提示:")
        print("   - 手动运行: python master_ai_scheduler.py")
        print("   - 查看日志: cat logs/master_ai_scheduler.log")
        print("   - 调整周期: 更新 ai_rules 表的 TRAINING_INTERVAL_DAYS")
    else:
        print("⚠️ 部分测试失败，请检查错误信息。")
    print("=" * 60 + "\n")
