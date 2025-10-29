# -*- coding: utf-8 -*-
"""
Child AI Agent - 执行分析层
负责：数据库检索、命盘模式识别、统计规律提取
"""

import os
import json
from typing import Dict, List, Any, Optional
from collections import Counter

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase SDK not available, Child AI using mock data", flush=True)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI SDK not available", flush=True)


class ChildAgent:
    """Child AI - 执行分析助手"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config["agents"]["child"]["name"]
        self.icon = config["agents"]["child"]["icon"]
        self.model = config["agents"]["child"]["model"]
        self.temperature = config["agents"]["child"]["temperature"]
        self.max_tokens = config["agents"]["child"]["max_tokens"]
        
        self.supabase_client = None
        if SUPABASE_AVAILABLE:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if url and key:
                self.supabase_client = create_client(url, key)
        
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LYNKER_MASTER_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
    
    def query_birthcharts(self, filters: Optional[Dict] = None) -> List[Dict]:
        """查询命盘数据库"""
        if not self.supabase_client:
            return self._mock_birthcharts()
        
        try:
            query = self.supabase_client.table("birthcharts").select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            resp = query.limit(self.config["database"]["max_query_results"]).execute()
            return resp.data or []
        except Exception as e:
            print(f"Error: Child AI query failed: {e}", flush=True)
            return self._mock_birthcharts()
    
    def query_match_results(self, user_id: Optional[int] = None) -> List[Dict]:
        """查询匹配结果"""
        if not self.supabase_client:
            return []
        
        try:
            query = self.supabase_client.table("match_results").select("*")
            
            if user_id:
                query = query.or_(f"user_a_id.eq.{user_id},user_b_id.eq.{user_id}")
            
            resp = query.limit(50).execute()
            return resp.data or []
        except Exception as e:
            print(f"Error: Child AI match results query failed: {e}", flush=True)
            return []
    
    def analyze_pattern(self, task: str) -> Dict[str, Any]:
        """执行命盘模式分析任务（真实命理逻辑）"""
        charts = self.query_birthcharts()
        
        if not charts:
            return {
                "status": "no_data",
                "message": "数据库暂无命盘数据",
                "patterns": {},
                "core_findings": []
            }
        
        main_stars = Counter()
        palaces = Counter()
        combinations = Counter()
        marriage_palace_stars = Counter()
        wealth_palace_stars = Counter()
        hualu_count = 0
        huaji_count = 0
        
        for chart in charts:
            birth_data = chart.get("birth_data", {})
            
            # 确保 birth_data 是字典类型
            if isinstance(birth_data, str):
                try:
                    birth_data = json.loads(birth_data)
                except:
                    birth_data = {}
            
            star = birth_data.get("main_star") or chart.get("main_star")
            palace = birth_data.get("ziwei_palace") or chart.get("ziwei_palace")
            marriage_star = birth_data.get("marriage_palace_star")
            wealth_star = birth_data.get("wealth_palace_star")
            transformations = birth_data.get("transformations", {})
            
            if star:
                main_stars[star] += 1
            if palace:
                palaces[palace] += 1
            if star and palace:
                combinations[f"{palace}-{star}"] += 1
            if marriage_star:
                marriage_palace_stars[marriage_star] += 1
            if wealth_star:
                wealth_palace_stars[wealth_star] += 1
            
            if transformations.get("hualu"):
                hualu_count += 1
            if transformations.get("huaji"):
                huaji_count += 1
        
        patterns = {
            "total_charts": len(charts),
            "top_stars": main_stars.most_common(5),
            "top_palaces": palaces.most_common(5),
            "top_combinations": combinations.most_common(5),
            "marriage_palace_distribution": marriage_palace_stars.most_common(5),
            "wealth_palace_distribution": wealth_palace_stars.most_common(5),
            "hualu_ratio": round(hualu_count / len(charts), 2) if len(charts) > 0 else 0,
            "huaji_ratio": round(huaji_count / len(charts), 2) if len(charts) > 0 else 0
        }
        
        core_findings = self._extract_core_findings(patterns)
        
        return {
            "status": "success",
            "agent": f"{self.icon} {self.name}",
            "task": task,
            "sample_size": len(charts),
            "patterns": patterns,
            "core_findings": core_findings,
            "summary": self._generate_summary(patterns)
        }
    
    def _generate_summary(self, patterns: Dict) -> str:
        """使用 AI 生成分析总结"""
        if not self.openai_client:
            return self._simple_summary(patterns)
        
        try:
            prompt = f"""你是 Child AI 执行助手，正在分析命盘数据库。

数据统计：
- 总命盘数：{patterns['total_charts']}
- 高频主星：{patterns['top_stars'][:3]}
- 高频命宫：{patterns['top_palaces'][:3]}
- 高频组合：{patterns['top_combinations'][:3]}

请用1-2句话总结关键发现（中文，专业术语）。
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Warning: Child AI summary generation failed: {e}", flush=True)
            return self._simple_summary(patterns)
    
    def _extract_core_findings(self, patterns: Dict) -> List[str]:
        """提取核心命理发现（优先三大核心指标）"""
        findings = []
        total = patterns.get("total_charts", 0)
        
        if total == 0:
            return findings
        
        top_star = patterns['top_stars'][0] if patterns['top_stars'] else None
        if top_star and top_star[1] / total > 0.15:
            findings.append(f"{top_star[0]}型命盘占比{int(top_star[1]/total*100)}%，显著高于平均")
        
        hualu_ratio = patterns.get("hualu_ratio", 0)
        if hualu_ratio > 0.5:
            findings.append(f"化禄比例偏高（{int(hualu_ratio*100)}%），整体运势较顺")
        
        huaji_ratio = patterns.get("huaji_ratio", 0)
        if huaji_ratio > 0.4:
            findings.append(f"化忌比例较高（{int(huaji_ratio*100)}%），需防破财或情感波折")
        
        if len(findings) < 3:
            marriage_stars = patterns.get("marriage_palace_distribution", [])
            if marriage_stars:
                top_marriage = marriage_stars[0]
                findings.append(f"夫妻宫以{top_marriage[0]}为主（{top_marriage[1]}例）")
        
        return findings[:3]
    
    def _simple_summary(self, patterns: Dict) -> str:
        """简单文本总结（无需 AI）"""
        top_star = patterns['top_stars'][0][0] if patterns['top_stars'] else "未知"
        top_palace = patterns['top_palaces'][0][0] if patterns['top_palaces'] else "未知"
        total = patterns.get('total_charts', 0)
        
        return f"数据库共{total}个命盘，主星以{top_star}为主，命宫多见{top_palace}。"
    
    def _mock_birthcharts(self) -> List[Dict]:
        """模拟数据（开发环境）"""
        return [
            {"id": 1, "name": "测试用户A", "main_star": "天府", "ziwei_palace": "巳"},
            {"id": 2, "name": "测试用户B", "main_star": "武曲", "ziwei_palace": "午"},
            {"id": 3, "name": "测试用户C", "main_star": "紫微", "ziwei_palace": "卯"}
        ]
    
    def process(self, task: str) -> str:
        """处理任务并返回结果"""
        result = self.analyze_pattern(task)
        
        if result["status"] == "no_data":
            return f"{self.icon} {self.name}: 暂无数据可分析。"
        
        return f"{self.icon} {self.name}: {result['summary']}"
