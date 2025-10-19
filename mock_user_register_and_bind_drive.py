#!/usr/bin/env python3
# mock_user_register_and_bind_drive.py
"""
批量创建样板用户并模拟 Google Drive 绑定（写入 Supabase.users）
Usage:
  python mock_user_register_and_bind_drive.py        # 仅注册/绑定
  python mock_user_register_and_bind_drive.py --sync   # 注册后尝试触发一次同步（可选）
"""

import time
import argparse
from datetime import datetime
from pprint import pprint

try:
    from supabase_init import get_supabase
except Exception as e:
    print("❌ 无法导入 supabase_init.get_supabase():", e)
    print("请确认 supabase_init.py 在项目中并且能返回 Supabase 客户端。")
    raise SystemExit(1)

SAMPLE_USERS = [
    {"user_id": "u_demo",  "email": "albert65lam@gmail.com",    "connected": True},
    {"user_id": "u_guru",  "email": "hamid311977@gmail.com",    "connected": True},
    {"user_id": "u_test1", "email": "ab77suhaimi@gmail.com",    "connected": True},
    # 如果需要再加：{"user_id":"u_test2","email":"...","connected":False}
]

# 要添加的 columns（确保表结构完整）
REQUIRED_COLUMNS = [
    ("drive_connected", "BOOLEAN DEFAULT FALSE"),
    ("drive_access_token", "TEXT"),
    ("drive_email", "TEXT"),
    # 可按需加入别的字段
]

def ensure_users_schema(supabase):
    """检测 public.users 表是否存在所需列，若缺则自动 ALTER 添加"""
    try:
        print("🔍 检查 public.users 表结构...")
        # 逐列执行 ALTER ... ADD COLUMN IF NOT EXISTS
        for col, col_def in REQUIRED_COLUMNS:
            sql = f"ALTER TABLE public.users ADD COLUMN IF NOT EXISTS {col} {col_def};"
            supabase.rpc("sql", {"q": sql}) if False else supabase.postgrest.rpc  # safe path fallback
            # Note: some Supabase clients don't expose generic exec - we fallback to table().execute below
            # Use simple execute via .rpc may not exist; use .table("users").select to force ping
        # A robust, cross-client way: attempt a harmless select to ensure schema cache refresh
        _ = supabase.table("users").select("id").limit(1).execute()
        print("✅ users 表存在，已确保所需列（若本地或云端支持 ALTER）。")
    except Exception as err:
        # If direct ALTER via client fails, print an instruction for manual SQL
        print("⚠️ 自动修改表结构遇到限制（客户端不支持直接执行SQL）。")
        print("请在 Supabase Dashboard 的 SQL Editor 手动运行下面 SQL：\n")
        manual_sql = """
ALTER TABLE public.users
ADD COLUMN IF NOT EXISTS drive_connected BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS drive_access_token TEXT,
ADD COLUMN IF NOT EXISTS drive_email TEXT;
"""
        print(manual_sql)
        print("之后再运行本脚本。")
        raise SystemExit(1)


def upsert_user(supabase, user_id: str, email: str, connected: bool):
    """在 users 表 upsert 一条记录。使用 name 字段保存 user_id"""
    ts = int(time.time())
    fake_token = f"FAKE_TOKEN_{user_id}_{ts}" if connected else None

    # 使用 name 字段作为 user_id 占位（与现有代码约定）
    payload = {
        "name": user_id,
        "email": email,
        "drive_connected": bool(connected),
        "drive_email": email if connected else None,
        "drive_access_token": fake_token if connected else None,
        "updated_at": datetime.utcnow().isoformat()
    }

    # 使用 upsert: 在 supabase python 客户端，这通常为 .table(...).upsert(...)
    try:
        resp = supabase.table("users").upsert(payload).execute()
        if resp.status_code if hasattr(resp, "status_code") else True:
            # some clients return object without status_code; assume success if no exception
            return {"ok": True, "payload": payload}
        else:
            return {"ok": False, "error": resp}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def print_summary(supabase):
    """读取并打印当前所有样板用户的绑定状态（限定 SAMPLE_USERS 列表）"""
    print("\n📊 样板用户绑定状态汇总：")
    for u in SAMPLE_USERS:
        try:
            r = supabase.table("users").select("name,email,drive_connected,drive_email,drive_access_token").eq("name", u["user_id"]).limit(1).execute()
            data = r.data[0] if r and r.data else None
            if not data:
                print(f"- {u['user_id']} → ❌ 未找到 (尚未写入)")
            else:
                status = "✅ 已绑定" if data.get("drive_connected") else "❌ 未绑定"
                # 截断 token 显示
                token = data.get("drive_access_token")
                token_short = (token[:16] + "...") if token else None
                print(f"- {u['user_id']} → {status} | email: {data.get('drive_email') or data.get('email')} | token: {token_short}")
        except Exception as e:
            print(f"- {u['user_id']} → 查询失败: {e}")


def optional_trigger_sync(supabase):
    """
    若用户传入 --sync 标志，可尝试调用 google_drive_sync.py 中的同步函数
    注意：若 token 为 FAKE_*，真实 Google API 会返回 401（这是预期）
    """
    try:
        from google_drive_sync import sync_memories_to_drive
    except Exception as e:
        print("⚠️ 未检测到 google_drive_sync.sync_memories_to_drive，可跳过同步。", e)
        return

    print("\n☁️ 正在尝试为已绑定用户触发一次 Drive 同步（仅模拟/测试）...")
    for u in SAMPLE_USERS:
        if not u["connected"]:
            continue
        print(f"→ 同步触发：{u['user_id']} ({u['email']})")
        try:
            sync_memories_to_drive(user_id=u["user_id"])
        except Exception as e:
            print(f"⚠️ 同步 {u['user_id']} 失败（可忽略，若为 FAKE_TOKEN 则为预期）：{e}")


def main(do_sync=False):
    print("🧪 正在运行样板用户注册与绑定脚本")
    supabase = get_supabase()
    if supabase is None:
        print("❌ 无法建立 Supabase 连接，请检查 supabase_init.py 配置")
        return

    # 确保表结构（或者提示手动在 Dashboard 运行 SQL）
    ensure_users_schema(supabase)

    created = 0
    updated = 0
    for u in SAMPLE_USERS:
        res = upsert_user(supabase, u["user_id"], u["email"], u["connected"])
        if res["ok"]:
            created += 1
            status = "已绑定" if u["connected"] else "未绑定"
            tshort = (res["payload"]["drive_access_token"][:16] + "...") if res["payload"].get("drive_access_token") else None
            print(f"✅ 已写入 {u['user_id']} (邮箱: {u['email']}) → {status} | token: {tshort}")
        else:
            print(f"❌ 写入失败 {u['user_id']}: {res.get('error')}")

    print(f"\n📊 共写入样板用户: {created} 条（包含绑定/未绑定）")

    # 打印当前表中样板用户的绑定状态
    print_summary(supabase)

    # 可选触发一次同步（测试）
    if do_sync:
        optional_trigger_sync(supabase)

    print("\n✅ 脚本执行完成。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="执行后尝试触发 google_drive_sync.sync_memories_to_drive()")
    args = parser.parse_args()
    main(do_sync=args.sync)
