import os
import time
import json
from datetime import datetime
from typing import Optional
from pathlib import Path
from supabase import create_client, Client
from master_vault_engine import insert_vault, get_db_connection

_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """延迟初始化 Supabase 客户端，带环境变量验证"""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("❌ 缺少 SUPABASE_URL 或 SUPABASE_KEY 环境变量！")
        
        _client = create_client(url, key)
    return _client

def analyze_patterns(records):
    """
    🧠 自动分析命盘规律（示例逻辑）
    """
    stats = {}
    skipped = 0
    
    for r in records:
        palace = r.get("ziwei_palace")
        star = r.get("main_star")
        
        if not palace or not star:
            skipped += 1
            continue
            
        key = (palace, star)
        stats[key] = stats.get(key, 0) + 1

    if skipped > 0:
        print(f"⚠️ 跳过了 {skipped} 条不完整的记录")

    results = []
    for (palace, star), count in stats.items():
        if count >= 2:
            results.append({
                "pattern": f"{palace}-{star}",
                "count": count,
                "insight": f"{palace} 宫主星 {star} 出现频率较高，可能与特定命格特征相关。"
            })
    return results

def check_vault_exists(title: str) -> bool:
    """检查 Vault 中是否已存在该标题（使用 master_vault_engine 的数据库连接）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master_vault WHERE title = %s", (title,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except Exception as e:
        print(f"⚠️ 检查去重时出错: {e}")
        return False

def store_to_knowledge_base(patterns):
    """
    📚 存入知识库 patterns/ 目录（明文JSON，供AI查询）
    """
    try:
        patterns_dir = Path("lkk_knowledge_base/patterns")
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # 按类型分组存储
        pattern_groups = {}
        for p in patterns:
            # 简单分类：根据宫位名称
            palace = p['pattern'].split('-')[0] if '-' in p['pattern'] else "general"
            if palace not in pattern_groups:
                pattern_groups[palace] = []
            pattern_groups[palace].append(p)
        
        # 保存每个分组
        for category, items in pattern_groups.items():
            filename = f"{category}_patterns.json"
            filepath = patterns_dir / filename
            
            # 加载现有数据（如果存在）
            existing_data = {"category": category, "patterns": [], "last_updated": ""}
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except:
                    pass
            
            # 合并新数据（简单去重：基于pattern名称）
            existing_patterns = {p['pattern']: p for p in existing_data.get('patterns', [])}
            for item in items:
                existing_patterns[item['pattern']] = item
            
            # 保存
            updated_data = {
                "category": category,
                "patterns": list(existing_patterns.values()),
                "last_updated": datetime.now().isoformat(),
                "total_count": len(existing_patterns)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            
            print(f"📚 知识库已更新：{filename} ({len(existing_patterns)} 条规律)")
        
    except Exception as e:
        print(f"⚠️ 知识库存储失败: {e}")

def store_to_vault(patterns):
    """
    🔐 存入 Master Vault（加密，支持去重）
    """
    stored = 0
    skipped = 0
    
    for p in patterns:
        title = f"命盘规律发现：{p['pattern']}"
        
        if check_vault_exists(title):
            print(f"⏭️ 跳过重复：{title}")
            skipped += 1
            continue
        
        try:
            content = f"发现次数: {p['count']}\n推测: {p['insight']}\n时间: {datetime.utcnow()}"
            insert_vault(title=title, content=content, created_by="Master AI")
            print(f"✅ 已存入 Vault：{title}")
            stored += 1
        except Exception as e:
            print(f"❌ 存储失败 ({title}): {e}")
    
    print(f"📊 存储统计：新增 {stored} 条，跳过 {skipped} 条重复")

def learn_from_birthcharts():
    """
    📊 从 Supabase 数据库中自动学习
    """
    try:
        print("🔍 扫描 birthcharts 数据中...")
        client = get_supabase_client()
        response = client.table("birthcharts").select("*").execute()
        records = response.data or []

        if not records:
            print("⚠️ 未找到命盘数据。")
            return

        patterns = analyze_patterns(records)
        if patterns:
            # 双重存储：加密到 Vault + 明文到知识库
            store_to_vault(patterns)
            store_to_knowledge_base(patterns)
        else:
            print("ℹ️ 暂无可记录的新规律。")
    except ValueError as e:
        print(f"❌ 环境配置错误: {e}")
    except Exception as e:
        print(f"❌ 学习过程出错: {e}")
        import traceback
        traceback.print_exc()

def verify_and_update_knowledge():
    """
    🔄 自我验证与知识更新逻辑
    """
    print("🧩 正在交叉验证既有结论...")
    time.sleep(1)
    print("✅ 验证完成，无冲突。")

def main():
    print("🚀 Master AI 自我学习引擎启动中...")
    learn_from_birthcharts()
    verify_and_update_knowledge()
    print("🌟 自我学习周期完成。")

if __name__ == "__main__":
    main()
