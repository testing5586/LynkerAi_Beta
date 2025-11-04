"""
Prophecy Validation Center - 预言验证中心路由
自动命盘预言生成、用户反馈记录与准确率统计

功能：
1. 根据紫微命盘生成预言问题
2. 记录用户反馈（准/不准）
3. 统计预言准确率
4. 数据归档到 JSONL 文件
"""

import os
import json
import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from pathlib import Path

from .prophecy_generator import generate_prophecies, analyze_prophecy_accuracy

bp = Blueprint("prophecy", __name__, url_prefix="/verify")

# 数据存储目录
DATA_DIR = Path(__file__).parent.parent / "data" / "prophecy"
DATA_DIR.mkdir(parents=True, exist_ok=True)
FEEDBACK_LOG_FILE = DATA_DIR / "prophecy_feedback_log.jsonl"


@bp.post("/api/run_prophecy_ai")
@login_required
def run_prophecy_ai():
    """
    生成预言问题
    
    接收：
        - ziwei_text: 紫微命盘文本（文墨天机格式）
        - bazi_text: 八字文本（可选）
    
    返回：
        - prophecies: 预言问题列表
    """
    data = request.get_json() or {}
    
    user_id = current_user.id  # 从当前登录用户获取
    ziwei_text = data.get("ziwei_text", "")
    bazi_text = data.get("bazi_text", "")
    
    print(f"[Prophecy] 为用户 {user_id} 生成预言问题...")
    print(f"[Prophecy] 紫微文本长度: {len(ziwei_text)} 字符")
    
    if not ziwei_text:
        return jsonify({
            "ok": False,
            "error": "缺少紫微命盘文本"
        }), 400
    
    try:
        prophecies = generate_prophecies(ziwei_text, bazi_text)
        print(f"[Prophecy] ✅ 生成 {len(prophecies)} 个预言问题")
        
        return jsonify({
            "ok": True,
            "prophecies": prophecies,
            "count": len(prophecies)
        })
    
    except Exception as e:
        print(f"[Prophecy] ❌ 生成失败: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


@bp.post("/api/record_prophecy_feedback")
@login_required
def record_prophecy_feedback():
    """
    记录用户对预言问题的反馈
    
    接收：
        - question: 预言问题文本
        - palace: 对应宫位
        - pattern: 星曜组合
        - result: "准" 或 "不准"
    
    返回：
        - ok: 是否成功
    """
    data = request.get_json() or {}
    
    user_id = current_user.id  # 从当前登录用户获取
    question = data.get("question")
    palace = data.get("palace", "未知")
    pattern = data.get("pattern", "未知")
    result = data.get("result")
    
    if not all([question, result]):
        return jsonify({
            "ok": False,
            "error": "缺少必要参数"
        }), 400
    
    # 构建记录条目
    entry = {
        "user_id": str(user_id),
        "question": question,
        "palace": palace,
        "pattern": pattern,
        "result": result,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    try:
        # 追加到 JSONL 文件
        with open(FEEDBACK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"[Prophecy] ✅ 记录反馈: {palace} - {result}")
        
        return jsonify({
            "ok": True,
            "message": "反馈已记录"
        })
    
    except Exception as e:
        print(f"[Prophecy] ❌ 记录失败: {e}")
        return jsonify({
            "ok": False,
            "error": str(e)
        }), 500


@bp.get("/api/prophecy_stats")
def prophecy_stats():
    """
    获取预言准确率统计
    
    返回：
        - total: 总预言数
        - correct: 准确数
        - accuracy: 准确率（百分比）
        - by_palace: 按宫位分类的准确率
    """
    records = []
    
    try:
        if FEEDBACK_LOG_FILE.exists():
            with open(FEEDBACK_LOG_FILE, "r", encoding="utf-8") as f:
                records = [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"[Prophecy] ⚠️ 读取统计数据失败: {e}")
    
    stats = analyze_prophecy_accuracy(records)
    
    print(f"[Prophecy] 📊 统计: {stats['total']} 条记录, {stats['accuracy']}% 准确率")
    
    return jsonify({
        "ok": True,
        **stats
    })


@bp.get("/api/prophecy_history/<user_id>")
def prophecy_history(user_id):
    """
    获取特定用户的预言历史记录
    
    Args:
        user_id: 用户ID
    
    返回：
        - records: 该用户的所有预言反馈记录
    """
    records = []
    
    try:
        if FEEDBACK_LOG_FILE.exists():
            with open(FEEDBACK_LOG_FILE, "r", encoding="utf-8") as f:
                all_records = [json.loads(line) for line in f if line.strip()]
                records = [r for r in all_records if r.get("user_id") == str(user_id)]
    except Exception as e:
        print(f"[Prophecy] ⚠️ 读取历史记录失败: {e}")
    
    return jsonify({
        "ok": True,
        "records": records,
        "count": len(records)
    })
