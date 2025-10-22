"""
AI Provider 性能监控与日志记录模块
记录每次 AI 调用的性能指标、成功率、token 使用等
"""

import os
import json
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime

LOG_FILE = "ai_usage_log.jsonl"
_lock = threading.Lock()


def log_ai_usage(
    provider: str,
    query: str,
    token_usage: Optional[Dict] = None,
    latency: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
    fallback_used: bool = False
):
    """
    记录 AI Provider 的调用统计
    
    Args:
        provider: 模型提供商 (chatgpt/gemini/glm/deepseek)
        query: 用户查询内容
        token_usage: Token 使用统计 (可选)
        latency: 响应延迟（秒）
        success: 是否成功
        error: 错误信息（如果失败）
        fallback_used: 是否使用了 fallback
    """
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "provider": provider,
        "query_preview": query[:60] + "..." if len(query) > 60 else query,
        "query_length": len(query),
        "token_usage": token_usage or {},
        "latency": round(latency, 3) if latency else None,
        "success": success,
        "error": error,
        "fallback_used": fallback_used
    }
    
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_ai_usage_logs(limit: int = 100) -> List[Dict]:
    """
    读取最近的 AI 使用日志
    
    Args:
        limit: 返回最近的 N 条记录
    
    Returns:
        日志记录列表
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    with _lock:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
    
    return [json.loads(line) for line in lines if line.strip()]


def summarize_ai_stats() -> Dict:
    """
    生成 AI Provider 统计汇总
    
    Returns:
        {
            "total_calls": int,
            "by_provider": {
                "chatgpt": {
                    "count": int,
                    "success_count": int,
                    "success_rate": float,
                    "avg_latency": float,
                    "total_tokens": int,
                    "fallback_count": int
                },
                ...
            },
            "recent_errors": [...]
        }
    """
    logs = get_ai_usage_logs(1000)
    
    if not logs:
        return {
            "total_calls": 0,
            "by_provider": {},
            "recent_errors": []
        }
    
    stats_by_provider = {}
    recent_errors = []
    
    for record in logs:
        provider = record["provider"]
        
        if provider not in stats_by_provider:
            stats_by_provider[provider] = {
                "count": 0,
                "success_count": 0,
                "latencies": [],
                "total_tokens": 0,
                "fallback_count": 0
            }
        
        provider_stats = stats_by_provider[provider]
        provider_stats["count"] += 1
        
        if record["success"]:
            provider_stats["success_count"] += 1
        else:
            if len(recent_errors) < 10:
                recent_errors.append({
                    "provider": provider,
                    "timestamp": record["timestamp"],
                    "error": record["error"],
                    "query": record["query_preview"]
                })
        
        if record["latency"] is not None:
            provider_stats["latencies"].append(record["latency"])
        
        if record["fallback_used"]:
            provider_stats["fallback_count"] += 1
        
        token_usage = record.get("token_usage", {})
        if isinstance(token_usage, dict):
            total = token_usage.get("total_tokens") or \
                    (token_usage.get("prompt_tokens", 0) + token_usage.get("completion_tokens", 0)) or \
                    (token_usage.get("input_tokens", 0) + token_usage.get("output_tokens", 0))
            provider_stats["total_tokens"] += total
    
    summary = {
        "total_calls": len(logs),
        "by_provider": {},
        "recent_errors": recent_errors
    }
    
    for provider, stats in stats_by_provider.items():
        summary["by_provider"][provider] = {
            "count": stats["count"],
            "success_count": stats["success_count"],
            "success_rate": round(stats["success_count"] / stats["count"] * 100, 1) if stats["count"] > 0 else 0,
            "avg_latency": round(sum(stats["latencies"]) / len(stats["latencies"]), 3) if stats["latencies"] else None,
            "total_tokens": stats["total_tokens"],
            "fallback_count": stats["fallback_count"],
            "fallback_rate": round(stats["fallback_count"] / stats["count"] * 100, 1) if stats["count"] > 0 else 0
        }
    
    return summary


def get_hourly_stats(hours: int = 24) -> List[Dict]:
    """
    获取按小时分组的统计数据
    
    Args:
        hours: 最近 N 小时
    
    Returns:
        按小时分组的统计列表
    """
    logs = get_ai_usage_logs(10000)
    
    if not logs:
        return []
    
    now = datetime.now()
    hourly_data = {}
    
    for record in logs:
        try:
            timestamp = datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S")
            hour_key = timestamp.strftime("%Y-%m-%d %H:00")
            
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {
                    "hour": hour_key,
                    "total": 0,
                    "success": 0,
                    "by_provider": {}
                }
            
            hourly_data[hour_key]["total"] += 1
            if record["success"]:
                hourly_data[hour_key]["success"] += 1
            
            provider = record["provider"]
            if provider not in hourly_data[hour_key]["by_provider"]:
                hourly_data[hour_key]["by_provider"][provider] = 0
            hourly_data[hour_key]["by_provider"][provider] += 1
        except:
            continue
    
    return sorted(hourly_data.values(), key=lambda x: x["hour"])


if __name__ == "__main__":
    print("📊 AI Provider 性能统计测试\n")
    
    log_ai_usage("chatgpt", "测试查询1", {"total_tokens": 150}, 2.5, True)
    log_ai_usage("gemini", "测试查询2", {"total_tokens": 200}, 1.8, True)
    log_ai_usage("chatgpt", "测试查询3", None, None, False, "API Key 错误")
    
    stats = summarize_ai_stats()
    print("统计汇总:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
