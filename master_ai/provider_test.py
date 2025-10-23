#!/usr/bin/env python3
"""
LynkerAI Provider 测试脚本
测试所有 Provider 的性能和可用性
"""
import time
from provider_manager import smart_chat, get_performance_report, ProviderManager

def test_all_providers():
    """测试所有 Provider"""
    print("=" * 70)
    print("  🧪 LynkerAI Multi-Provider 测试")
    print("=" * 70)
    print()
    
    test_queries = [
        "你好，请简单介绍一下你自己",
        "1+1等于几？",
        "什么是LynkerAI？",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 测试 {i}/{len(test_queries)}: {query}")
        print("-" * 70)
        
        response, provider, response_time = smart_chat(query)
        
        print(f"🤖 Provider: {provider.upper()}")
        print(f"⏱️  响应时间: {response_time:.2f}s")
        print(f"💬 回复: {response[:150]}...")
        
        time.sleep(1)
    
    print("\n" + "=" * 70)
    print("  ✅ 测试完成")
    print("=" * 70)
    print()
    
    print(get_performance_report())


def stress_test(num_requests: int = 10):
    """压力测试"""
    print(f"\n🔥 压力测试: {num_requests} 个请求")
    print("=" * 70)
    
    queries = [
        "你好",
        "1+1=?",
        "今天天气",
        "LynkerAI",
        "命理",
    ]
    
    for i in range(num_requests):
        query = queries[i % len(queries)]
        print(f"\r📊 进度: {i+1}/{num_requests}", end="", flush=True)
        
        smart_chat(query)
        time.sleep(0.5)
    
    print("\n✅ 压力测试完成\n")
    print(get_performance_report())


def reset_all_stats():
    """重置统计数据"""
    manager = ProviderManager()
    manager.reset_stats()
    print("✅ 统计数据已重置")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stress":
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            stress_test(num)
        elif sys.argv[1] == "reset":
            reset_all_stats()
        elif sys.argv[1] == "report":
            print(get_performance_report())
        else:
            print("用法:")
            print("  python provider_test.py          # 运行基础测试")
            print("  python provider_test.py stress 10 # 压力测试(10次)")
            print("  python provider_test.py reset     # 重置统计")
            print("  python provider_test.py report    # 查看报告")
    else:
        test_all_providers()
