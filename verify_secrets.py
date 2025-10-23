#!/usr/bin/env python3
"""
LynkerAI 密钥验证脚本
验证 TMS_SECRET_KEY 和 LYNKER_MASTER_KEY 是否正确配置
"""
import os
import sys

def check_secret_exists(key_name):
    """检查密钥是否存在（不显示值）"""
    value = os.environ.get(key_name)
    if value:
        length = len(value)
        return True, length
    return False, 0

def test_tms_signature():
    """测试 TMS 签章功能"""
    sys.path.insert(0, 'master_ai')
    try:
        from master_validator import create_signature, verify_signature
        
        # 测试数据
        public_key = "test_child_ai"
        payload = "test_chart_data_12345"
        
        # 生成签章
        signature = create_signature(public_key, payload)
        
        # 验证签章
        is_valid = verify_signature(public_key, payload, signature)
        
        return is_valid, signature[:30] + "..."
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("  🔐 LynkerAI 密钥验证工具")
    print("=" * 70)
    print()
    
    # 检查 TMS_SECRET_KEY
    print("1️⃣ 检查 TMS_SECRET_KEY...")
    exists, length = check_secret_exists("TMS_SECRET_KEY")
    if exists:
        print(f"   ✅ 已配置 (长度: {length} 字符)")
        if length >= 32:
            print(f"   ✅ 密钥强度: 安全 (推荐 ≥32 字符)")
        else:
            print(f"   ⚠️  密钥强度: 较弱 (建议至少 32 字符)")
    else:
        print(f"   ❌ 未配置")
        return False
    
    print()
    
    # 检查 LYNKER_MASTER_KEY
    print("2️⃣ 检查 LYNKER_MASTER_KEY...")
    exists, length = check_secret_exists("LYNKER_MASTER_KEY")
    if exists:
        print(f"   ✅ 已配置 (长度: {length} 字符)")
        if length >= 32:
            print(f"   ✅ 密钥强度: 安全")
        else:
            print(f"   ⚠️  密钥强度: 较弱")
    else:
        print(f"   ❌ 未配置")
        return False
    
    print()
    
    # 测试 TMS 签章功能
    print("3️⃣ 测试 TMS 签章功能...")
    try:
        is_valid, signature = test_tms_signature()
        if is_valid:
            print(f"   ✅ 签章生成/验证成功")
            print(f"   📝 示例签章: {signature}")
        else:
            print(f"   ❌ 签章验证失败: {signature}")
            return False
    except Exception as e:
        print(f"   ❌ 测试出错: {e}")
        return False
    
    print()
    
    # 检查其他相关密钥
    print("4️⃣ 检查其他已配置的密钥...")
    other_keys = [
        "OPENAI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_KEY",
        "DATABASE_URL"
    ]
    
    for key in other_keys:
        exists, length = check_secret_exists(key)
        if exists:
            print(f"   ✅ {key} (长度: {length})")
        else:
            print(f"   ℹ️  {key} (未配置)")
    
    print()
    print("=" * 70)
    print("  🎉 验证完成！所有关键密钥已正确配置")
    print("=" * 70)
    print()
    print("💡 下一步:")
    print("   1. 启动 TMS 验证器: cd master_ai && python master_validator.py")
    print("   2. 运行完整演示: cd master_ai && python demo_tms.py")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
