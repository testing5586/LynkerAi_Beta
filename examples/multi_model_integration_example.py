"""
Multi-Model Dispatcher 集成示例
演示如何在各种场景中使用智能模型选择系统
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multi_model_dispatcher import get_model_for_user, get_api_key_for_user, load_ai_rules

def example_1_basic_usage():
    """示例 1: 基础使用"""
    print("=== 示例 1: 基础使用 ===\n")
    
    user_id = 2
    model = get_model_for_user(user_id)
    api_key = get_api_key_for_user(user_id)
    
    print(f"用户 {user_id} 使用模型: {model}")
    print(f"API Key 前缀: {api_key[:20] if api_key else 'None'}...\n")

def example_2_openai_integration():
    """示例 2: 集成到 OpenAI 调用"""
    print("=== 示例 2: OpenAI 集成 ===\n")
    
    print("代码示例:")
    print("""
    import openai
    from multi_model_dispatcher import get_model_for_user, get_api_key_for_user
    
    def call_ai_for_user(user_id: int, prompt: str):
        model = get_model_for_user(user_id)
        api_key = get_api_key_for_user(user_id)
        
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    """)
    print("💡 提示: 这样可以自动为每个用户选择合适的模型\n")

def example_3_batch_processing():
    """示例 3: 批量处理多个用户"""
    print("=== 示例 3: 批量处理 ===\n")
    
    user_ids = [1, 2, 3, 4, 5]
    
    print("用户模型分配:")
    for uid in user_ids:
        model = get_model_for_user(uid)
        print(f"  用户 {uid} → {model}")
    
    print()

def example_4_config_management():
    """示例 4: 配置管理"""
    print("=== 示例 4: 配置管理 ===\n")
    
    rules = load_ai_rules()
    
    print("当前 AI 规则配置:")
    for key, value in rules.items():
        print(f"  {key}: {value}")
    
    print("\n💡 提示: 可以在 Supabase ai_rules 表中更新这些配置")
    print("   更新后无需重启系统即可生效！\n")

def example_5_master_ai_integration():
    """示例 5: 集成到 Master AI Reasoner"""
    print("=== 示例 5: Master AI Reasoner 集成 ===\n")
    
    def master_ai_reason_user(user_id: int):
        """使用正确的模型为用户推理"""
        model = get_model_for_user(user_id)
        api_key = get_api_key_for_user(user_id)
        
        print(f"🧠 Master AI 推理引擎启动...")
        print(f"   用户: {user_id}")
        print(f"   模型: {model}")
        print(f"   API Key: {'LYNKER_MASTER_KEY' if 'LYNKER' in str(api_key) else 'User Key'}")
        print(f"   状态: 就绪")
        
    master_ai_reason_user(2)
    print()

def example_6_cost_optimization():
    """示例 6: 成本优化建议"""
    print("=== 示例 6: 成本优化建议 ===\n")
    
    print("💰 模型成本对比:")
    print("  gpt-4o-mini:  $0.15 / 1M tokens (输入)")
    print("  gpt-4-turbo:  $10.00 / 1M tokens (输入)")
    print()
    print("📊 建议策略:")
    print("  ✅ Free 用户 → gpt-4o-mini (低成本)")
    print("  ✅ Pro 用户 → gpt-4-turbo (高质量)")
    print("  ✅ Admin → gpt-4-turbo (最佳性能)")
    print()
    print("💡 优化技巧:")
    print("  1. 使用 max_tokens 限制响应长度")
    print("  2. 缓存常见查询结果")
    print("  3. 批量处理降低 API 调用次数")
    print()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Multi-Model Dispatcher 集成示例")
    print("="*60 + "\n")
    
    example_1_basic_usage()
    example_2_openai_integration()
    example_3_batch_processing()
    example_4_config_management()
    example_5_master_ai_integration()
    example_6_cost_optimization()
    
    print("="*60)
    print("✅ 所有示例运行完成！")
    print("📚 更多信息请查看: MULTI_MODEL_DISPATCHER_GUIDE.md")
    print("="*60 + "\n")
