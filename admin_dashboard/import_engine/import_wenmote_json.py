"""
文墨天机 JSON 批量导入器
Wenmote JSON Batch Importer - 命令行 & HTTP 二用
"""

import os
import json
import glob
from supabase import create_client
from .normalize_chart import normalize_from_wenmote

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
sb = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def import_one_json(path):
    """导入单个 JSON 文件"""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    norm = normalize_from_wenmote(raw)
    
    if not sb:
        raise Exception("Supabase 客户端未初始化")
    
    resp = sb.table("birthcharts").insert({
        "name": norm["name"],
        "gender": norm["gender"],
        "birth_time": norm["birth_time"],
        "ziwei_palace": None,
        "main_star": None,
        "shen_palace": None,
        "birth_data": norm["birth_data"]
    }).execute()
    
    return resp.data

def import_dir_json(dirpath):
    """批量导入目录下所有 JSON 文件"""
    files = glob.glob(os.path.join(dirpath, "*.json"))
    results = []
    
    for fp in files:
        try:
            data = import_one_json(fp)
            results.append({"file": os.path.basename(fp), "ok": True, "data": data})
        except Exception as e:
            results.append({"file": os.path.basename(fp), "ok": False, "error": str(e)})
    
    return results

if __name__ == "__main__":
    import argparse
    
    p = argparse.ArgumentParser(description="批量导入文墨 JSON → Supabase.birthcharts")
    p.add_argument("--dir", required=True, help="包含文墨 JSON 的目录")
    args = p.parse_args()
    
    res = import_dir_json(args.dir)
    ok = sum(1 for r in res if r["ok"])
    fail = len(res) - ok
    
    print(f"✅ 导入完成：成功 {ok}，失败 {fail}")
    for r in res:
        print(("✓" if r["ok"] else "✗"), r["file"], r.get("error", ""))
