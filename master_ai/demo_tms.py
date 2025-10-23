"""
LynkerAI TMS 演示脚本
展示签章生成、验证和置信投票流程
"""
import requests
import json
import time

TMS_BASE = "http://localhost:8080"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def demo_sign_and_verify():
    """演示：生成签章并验证"""
    print_section("1️⃣ 演示：命盘签章生成与验证")
    
    # 步骤 1: 生成签章
    print("📝 步骤 1: Child AI 为命盘生成签章...")
    chart_data = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "location": "北京",
        "longitude": 116.4074,
        "latitude": 39.9042
    }
    
    response = requests.post(f"{TMS_BASE}/api/tms/sign", json={
        "public_key": "child_ai_bazi_001",
        "chart_data": chart_data
    })
    
    if response.status_code == 200:
        sign_data = response.json()
        print(f"✅ 签章生成成功:")
        print(f"   命盘哈希: {sign_data['chart_hash'][:32]}...")
        print(f"   签章: {sign_data['signature'][:40]}...")
        print(f"   时间戳: {sign_data['timestamp']}")
        
        # 步骤 2: 验证签章
        print(f"\n🔐 步骤 2: Master AI 验证签章...")
        verify_response = requests.post(f"{TMS_BASE}/api/tms/verify", json={
            "public_key": sign_data['public_key'],
            "payload": sign_data['chart_hash'],
            "signature": sign_data['signature']
        })
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            print(f"✅ 验证成功:")
            print(f"   验证状态: {verify_data['verified']}")
            print(f"   验证者: {verify_data['verifier']}")
            print(f"   验证时间: {verify_data['timestamp']}")
        else:
            print(f"❌ 验证失败: {verify_response.json()}")
    else:
        print(f"❌ 签章生成失败: {response.json()}")

def demo_invalid_signature():
    """演示：伪造签章验证失败"""
    print_section("2️⃣ 演示：伪造签章验证失败")
    
    print("🚨 尝试使用伪造的签章...")
    response = requests.post(f"{TMS_BASE}/api/tms/verify", json={
        "public_key": "malicious_ai",
        "payload": "fake_chart_hash",
        "signature": "AI_fake_signature_12345"
    })
    
    if response.status_code == 403:
        print(f"✅ 系统正确拒绝了伪造签章:")
        print(f"   {response.json()}")
    else:
        print(f"⚠️ 意外结果: {response.json()}")

def demo_health_check():
    """演示：健康检查"""
    print_section("3️⃣ 演示：系统健康检查")
    
    response = requests.get(f"{TMS_BASE}/api/tms/health")
    
    if response.status_code == 200:
        health = response.json()
        print(f"✅ 系统运行正常:")
        print(f"   服务: {health['service']}")
        print(f"   版本: {health['version']}")
        print(f"   状态: {health['status']}")
        print(f"   时间: {health['timestamp']}")
    else:
        print(f"❌ 健康检查失败")

def demo_multi_ai_workflow():
    """演示：多 Child AI 协作流程"""
    print_section("4️⃣ 演示：多 Child AI 协作验证")
    
    child_ais = ["child_ai_bazi", "child_ai_ziwei", "child_ai_qimen"]
    chart_data = {
        "birth_date": "1985-12-20",
        "birth_time": "08:15",
        "location": "上海"
    }
    
    signatures = []
    
    # 每个 Child AI 生成自己的签章
    for ai_id in child_ais:
        print(f"\n🤖 {ai_id} 正在分析命盘...")
        response = requests.post(f"{TMS_BASE}/api/tms/sign", json={
            "public_key": ai_id,
            "chart_data": chart_data
        })
        
        if response.status_code == 200:
            sign_data = response.json()
            signatures.append(sign_data)
            print(f"   ✅ 签章生成成功")
        else:
            print(f"   ❌ 签章生成失败")
    
    # 验证所有签章
    print(f"\n🔐 Master AI 验证所有 Child AI 的签章...")
    verified_count = 0
    for sign in signatures:
        verify_response = requests.post(f"{TMS_BASE}/api/tms/verify", json={
            "public_key": sign['public_key'],
            "payload": sign['chart_hash'],
            "signature": sign['signature']
        })
        
        if verify_response.status_code == 200:
            verified_count += 1
    
    print(f"\n✅ 验证完成: {verified_count}/{len(signatures)} 个签章有效")
    print(f"   置信度: {(verified_count/len(signatures)*100):.1f}%")

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   LynkerAI TMS v1.0 - Trusted Metaphysics System Demo   ║
    ║                假名制 × 真命盘验证 × 签章验证              ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查 TMS 服务是否运行
    try:
        response = requests.get(f"{TMS_BASE}/api/tms/health", timeout=2)
        if response.status_code != 200:
            print("❌ TMS 服务未响应，请先启动:")
            print("   cd master_ai && python master_validator.py")
            exit(1)
    except Exception:
        print("❌ 无法连接到 TMS 服务 (http://localhost:8080)")
        print("   请先启动: cd master_ai && python master_validator.py")
        exit(1)
    
    try:
        demo_health_check()
        time.sleep(1)
        
        demo_sign_and_verify()
        time.sleep(1)
        
        demo_invalid_signature()
        time.sleep(1)
        
        demo_multi_ai_workflow()
        
        print_section("🎉 演示完成")
        print("📚 查看完整文档: master_ai/README_TMS_v1.md")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示已中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
