#!/usr/bin/env python3
"""
LynkerAI Multi-Provider 调度系统 v1.0
智能切换 ChatGPT / Gemini / GLM / DeepSeek
"""
import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multi_model_ai import MultiModelAI

STATS_FILE = "master_ai/provider_stats.json"

class ProviderManager:
    """AI Provider 智能调度管理器"""
    
    PROVIDERS = ["chatgpt", "gemini", "glm", "deepseek"]
    
    def __init__(self, stats_file: str = STATS_FILE):
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """加载性能统计数据"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "providers": {
                provider: {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "total_response_time": 0.0,
                    "avg_response_time": 0.0,
                    "success_rate": 0.0,
                    "last_used": None,
                    "last_status": "未使用"
                }
                for provider in self.PROVIDERS
            },
            "total_requests": 0,
            "last_updated": None
        }
    
    def _save_stats(self):
        """保存统计数据"""
        self.stats["last_updated"] = datetime.now().isoformat()
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 无法保存统计数据: {e}")
    
    def record_request(self, provider: str, success: bool, response_time: float):
        """记录请求结果"""
        if provider not in self.stats["providers"]:
            return
        
        p_stats = self.stats["providers"][provider]
        p_stats["total_requests"] += 1
        
        if success:
            p_stats["successful_requests"] += 1
            p_stats["total_response_time"] += response_time
            p_stats["avg_response_time"] = (
                p_stats["total_response_time"] / p_stats["successful_requests"]
            )
            p_stats["last_status"] = "成功"
        else:
            p_stats["failed_requests"] += 1
            p_stats["last_status"] = "失败"
        
        p_stats["success_rate"] = (
            p_stats["successful_requests"] / p_stats["total_requests"] * 100
        )
        p_stats["last_used"] = datetime.now().isoformat()
        
        self.stats["total_requests"] += 1
        self._save_stats()
    
    def get_provider_stats(self, provider: str) -> Dict:
        """获取单个 Provider 的统计信息"""
        return self.stats["providers"].get(provider, {})
    
    def get_all_stats(self) -> Dict:
        """获取所有统计信息"""
        return self.stats
    
    def get_best_provider(self) -> str:
        """获取当前最优 Provider"""
        best_provider = "chatgpt"
        best_score = -1
        
        for provider in self.PROVIDERS:
            stats = self.stats["providers"][provider]
            
            if stats["total_requests"] == 0:
                score = 50
            else:
                success_rate = stats["success_rate"]
                avg_time = stats["avg_response_time"] if stats["avg_response_time"] > 0 else 5
                
                speed_score = max(0, 100 - avg_time * 10)
                score = success_rate * 0.7 + speed_score * 0.3
            
            if score > best_score:
                best_score = score
                best_provider = provider
        
        return best_provider
    
    def reset_stats(self):
        """重置所有统计数据"""
        self.stats = self._load_stats()
        self._save_stats()


def smart_chat(query: str, context: str = "", provider: str = "chatgpt") -> Tuple[str, str, float]:
    """
    智能聊天（带性能记录）
    
    Args:
        query: 用户查询
        context: 上下文（可选）
        provider: 指定 Provider，留空则自动选择
    
    Returns:
        (response, provider_used, response_time)
    """
    manager = ProviderManager()
    
    if not provider:
        provider = manager.get_best_provider()
    
    full_prompt = f"{context}\n\n{query}" if context else query
    
    result = MultiModelAI.call(provider, full_prompt, enable_fallback=True)
    
    success = result["success"]
    provider_used = result["provider"]
    response = result["answer"] or result["error"]
    response_time = result["latency"]
    
    manager.record_request(provider_used, success, response_time)
    
    return response, provider_used, response_time


def get_performance_report() -> str:
    """生成性能报告（终端输出）"""
    manager = ProviderManager()
    stats = manager.get_all_stats()
    
    report = []
    report.append("=" * 70)
    report.append("  🧠 LynkerAI Multi-Provider 性能报告")
    report.append("=" * 70)
    report.append("")
    report.append(f"📊 总请求数: {stats['total_requests']}")
    report.append(f"🕐 最后更新: {stats['last_updated'] or '无'}")
    report.append("")
    report.append("-" * 70)
    
    for provider in ProviderManager.PROVIDERS:
        p_stats = stats["providers"][provider]
        report.append(f"\n🤖 Provider: {provider.upper()}")
        report.append(f"   总请求: {p_stats['total_requests']}")
        report.append(f"   成功率: {p_stats['success_rate']:.1f}%")
        report.append(f"   平均响应时间: {p_stats['avg_response_time']:.2f}s")
        report.append(f"   最后使用: {p_stats['last_used'] or '未使用'}")
        report.append(f"   状态: {p_stats['last_status']}")
    
    report.append("")
    report.append("-" * 70)
    report.append(f"✨ 推荐 Provider: {manager.get_best_provider().upper()}")
    report.append("=" * 70)
    
    return "\n".join(report)


if __name__ == "__main__":
    print(get_performance_report())
