#!/usr/bin/env python3
"""
==========================================================
Google Drive 同步模块 - 上传 AI 记忆到用户个人云端
==========================================================
功能：
1. 使用用户的 Google Drive access_token 上传文件
2. 支持将 child_ai_memory 数据同步到 Google Drive
3. 自动创建 "LynkerAI_Memories" 文件夹
4. 支持增量更新和版本管理
"""

import json
import requests
from datetime import datetime


def upload_to_google_drive(access_token, file_name, file_content, mime_type="application/json"):
    """
    上传文件到 Google Drive
    
    参数:
        access_token: Google OAuth 访问令牌
        file_name: 文件名
        file_content: 文件内容（字符串或字节）
        mime_type: MIME 类型
    
    返回:
        上传结果字典
    """
    
    # 1. 检查或创建 LynkerAI_Memories 文件夹
    folder_id = get_or_create_folder(access_token, "LynkerAI_Memories")
    
    if not folder_id:
        return {"success": False, "error": "无法创建文件夹"}
    
    # 2. 上传文件
    metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    
    files = {
        "data": ("metadata", json.dumps(metadata), "application/json"),
        "file": (file_name, file_content, mime_type)
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers=headers,
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文件已上传到 Google Drive：{file_name}")
            return {"success": True, "file_id": result.get("id"), "name": file_name}
        else:
            print(f"❌ 上传失败：{response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ 上传异常：{e}")
        return {"success": False, "error": str(e)}


def get_or_create_folder(access_token, folder_name):
    """
    获取或创建 Google Drive 文件夹
    
    参数:
        access_token: Google OAuth 访问令牌
        folder_name: 文件夹名称
    
    返回:
        文件夹 ID
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 1. 检查文件夹是否存在
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        response = requests.get(
            f"https://www.googleapis.com/drive/v3/files?q={query}",
            headers=headers
        )
        
        if response.status_code == 200:
            files = response.json().get("files", [])
            
            if files:
                print(f"✅ 找到已存在的文件夹：{folder_name}")
                return files[0]["id"]
        
        # 2. 创建新文件夹
        metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        
        response = requests.post(
            "https://www.googleapis.com/drive/v3/files",
            headers=headers,
            json=metadata
        )
        
        if response.status_code == 200:
            folder_id = response.json().get("id")
            print(f"✅ 已创建新文件夹：{folder_name}")
            return folder_id
        else:
            print(f"❌ 创建文件夹失败：{response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 文件夹操作异常：{e}")
        return None


def sync_memories_to_drive(user_id, memories_data, access_token):
    """
    同步用户的 AI 记忆到 Google Drive
    
    参数:
        user_id: 用户ID
        memories_data: 记忆数据（列表或字典）
        access_token: Google OAuth 访问令牌
    
    返回:
        同步结果
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"lynker_ai_memories_{user_id}_{timestamp}.json"
    
    # 准备文件内容
    file_content = json.dumps({
        "user_id": user_id,
        "timestamp": timestamp,
        "memories_count": len(memories_data) if isinstance(memories_data, list) else 1,
        "data": memories_data
    }, ensure_ascii=False, indent=2)
    
    # 上传到 Google Drive
    result = upload_to_google_drive(
        access_token=access_token,
        file_name=file_name,
        file_content=file_content.encode("utf-8"),
        mime_type="application/json"
    )
    
    return result


def test_google_drive_connection(access_token):
    """
    测试 Google Drive 连接
    
    参数:
        access_token: Google OAuth 访问令牌
    
    返回:
        True 如果连接成功，否则 False
    """
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            "https://www.googleapis.com/drive/v3/about?fields=user",
            headers=headers
        )
        
        if response.status_code == 200:
            user_info = response.json().get("user", {})
            print(f"✅ Google Drive 连接成功！用户：{user_info.get('emailAddress')}")
            return True
        else:
            print(f"❌ 连接失败：{response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 连接异常：{e}")
        return False


# ============================================================
# 测试代码
# ============================================================
if __name__ == "__main__":
    print("🧪 测试 Google Drive 同步模块\n")
    print("⚠️ 本模块需要有效的 Google OAuth access_token")
    print("💡 请在前端完成授权后获取 access_token 进行测试\n")
    
    # 测试数据
    test_memories = [
        {
            "partner_id": "u_test1",
            "summary": "命格高度共振，彼此能深刻理解。",
            "tags": ["设计行业", "晚婚", "母缘浅"],
            "similarity": 0.911
        },
        {
            "partner_id": "u_test2",
            "summary": "命理特征有一定相似性，适合轻交流。",
            "tags": ["母缘浅", "无子女"],
            "similarity": 0.756
        }
    ]
    
    print("📋 测试数据准备完成")
    print(f"   - 记忆数量：{len(test_memories)}")
    print("\n💡 使用方法：")
    print("   1. 在前端完成 Google OAuth 授权")
    print("   2. 获取 access_token")
    print("   3. 调用 sync_memories_to_drive(user_id, memories, access_token)")
    print("\n示例代码：")
    print('   token = "YOUR_ACCESS_TOKEN"')
    print('   result = sync_memories_to_drive("u_demo", test_memories, token)')
    print('   print(result)')
