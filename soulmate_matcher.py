# ==========================================================
# LynkerAI Soulmate Matcher - 同命匹配系统
# ==========================================================

from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from supabase_init import init_supabase
import torch

# ----------------------------------------------------------
# 初始化语义模型（复用免费中文模型）
# ----------------------------------------------------------
print("🧠 Loading Chinese semantic model for soulmate matching...")
model = SentenceTransformer("shibing624/text2vec-base-chinese")
print("✅ Soulmate matcher model loaded!")

# ----------------------------------------------------------
# 自动建表逻辑
# ----------------------------------------------------------
def init_match_table(supabase):
    """自动检测并创建匹配结果表"""
    if supabase is None:
        print("⚠️ Supabase 未连接。")
        return
    
    try:
        # 尝试查询表，检查是否存在
        supabase.table("soulmate_matches").select("id").limit(1).execute()
        print("✅ Table 'soulmate_matches' already exists.")
    except Exception as e:
        print("🛠️ Table 'soulmate_matches' not found, it may need to be created manually.")
        print("📋 Please create it using the SQL editor in Supabase Dashboard if needed.")
        print("💡 SQL schema available in: supabase_tables_schema.sql")

# ----------------------------------------------------------
# 相似度计算
# ----------------------------------------------------------
def compute_similarity(tags1, tags2):
    """计算两位用户的 life_tags 相似度"""
    # 将所有标签值转换为文本
    t1 = " ".join([str(v) for v in tags1.values() if v])
    t2 = " ".join([str(v) for v in tags2.values() if v])
    
    if not t1 or not t2:
        return 0.0
    
    # 使用语义模型计算相似度
    emb1 = model.encode(t1, convert_to_tensor=True)
    emb2 = model.encode(t2, convert_to_tensor=True)
    sim = util.cos_sim(emb1, emb2).item()
    return round(sim, 3)

# ----------------------------------------------------------
# 主匹配函数
# ----------------------------------------------------------
def run_soulmate_matcher(user_id="u_demo", supabase=None, top_n=3):
    """
    执行同命匹配
    参数：
        user_id: 目标用户ID
        supabase: Supabase 客户端（可选）
        top_n: 返回前 N 个最匹配的用户
    返回：
        匹配结果列表
    """
    print("\n💞 正在执行同命匹配 Soulmate Matcher ...")

    # 初始化 Supabase（如果未提供）
    if supabase is None:
        supabase = init_supabase()
    
    # 检查匹配表
    init_match_table(supabase)
    
    if supabase is None:
        print("⚠️ Supabase 未连接，无法执行匹配。")
        return None

    # 读取所有用户的 life_tags
    try:
        response = supabase.table("user_life_tags").select("*").execute()
        data = response.data
    except Exception as e:
        print(f"⚠️ 读取用户标签失败：{e}")
        return None
    
    if not data or len(data) < 2:
        print("⚠️ 数据不足（需要至少 2 个用户），无法执行匹配。")
        return None

    # 找到目标用户
    current = next((u for u in data if u["user_id"] == user_id), None)
    if not current:
        print(f"⚠️ 未找到用户 {user_id} 的 life_tags。")
        return None

    print(f"🔍 正在为用户 {user_id} 匹配同命...")
    
    # 计算与其他用户的相似度
    results = []
    for other in data:
        if other["user_id"] == user_id:
            continue
        
        sim = compute_similarity(current, other)
        
        # 找出共同标签
        shared = {
            k: v for k, v in current.items() 
            if k in other and k not in ["id", "user_id", "created_at", "updated_at"]
            and current[k] == other[k] and v
        }
        
        results.append({
            "matched_user_id": other["user_id"],
            "similarity": sim,
            "shared_tags": shared
        })

    # 按相似度排序，取前 N 个
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_n]

    # 保存匹配结果到数据库
    for r in results:
        try:
            supabase.table("soulmate_matches").upsert({
                "user_id": user_id,
                "matched_user_id": r["matched_user_id"],
                "similarity": r["similarity"],
                "shared_tags": r["shared_tags"],
                "verified_at": datetime.now().isoformat()
            }).execute()
            print(f"💗 匹配保存：{user_id} ↔ {r['matched_user_id']} (相似度：{r['similarity']})")
        except Exception as e:
            print(f"⚠️ 保存匹配结果失败：{e}")

    print(f"✅ Soulmate 匹配完成，找到 {len(results)} 个匹配用户。")
    
    return {
        "user_id": user_id,
        "matches": results,
        "total_matched": len(results),
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ----------------------------------------------------------
# 测试
# ----------------------------------------------------------
if __name__ == "__main__":
    result = run_soulmate_matcher("u_demo", top_n=5)
    if result:
        print("\n匹配结果：")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
