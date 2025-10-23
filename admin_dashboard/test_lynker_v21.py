#!/usr/bin/env python3
"""
Lynker Engine v2.1 测试脚本
测试动态命理分析核心的完整协作链
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from lynker_engine import LynkerEngine

def test_astrological_analysis():
    """测试命理规律分析"""
    print("=" * 60)
    print("🧪 测试 Lynker Engine v2.1 - 动态命理分析核心")
    print("=" * 60)
    
    engine = LynkerEngine()
    
    print("\n📊 测试查询：分析命盘数据库的化禄化忌规律\n")
    
    result = engine.process_query("分析命盘数据库的化禄化忌规律")
    
    print("\n" + "=" * 60)
    print("🤖 Child AI 分析结果：")
    print("=" * 60)
    print(result.get("child", "无"))
    
    print("\n" + "=" * 60)
    print("🧩 Group Leader 协调报告：")
    print("=" * 60)
    print(result.get("leader", "无"))
    
    print("\n" + "=" * 60)
    print("🧠 Master AI 推理结论：")
    print("=" * 60)
    print(result.get("master", "无"))
    
    print("\n" + "=" * 60)
    print("📈 系统状态：")
    print("=" * 60)
    print(f"✅ 置信度：{result.get('confidence', 0):.2%}")
    print(f"✅ 样本量：{result.get('sample_size', 0)} 份")
    print(f"✅ Vault 已存储：{'是' if result.get('vault_saved') else '否'}")
    print(f"✅ Superintendent 已通知：{'是' if result.get('superintendent_notified') else '否'}")
    
    print("\n" + "=" * 60)
    print("🎯 测试完成")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    try:
        test_astrological_analysis()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
