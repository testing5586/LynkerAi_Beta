"""
检索路由器 - 关键词检索引擎
支持从 rules/patterns/case_study 三层知识库检索相关内容
"""
import os
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class RetrievalRouter:
    """
    关键词检索路由器
    使用 keyword + regex 触发，返回增强上下文
    """
    
    def __init__(self, base_path: str = "lkk_knowledge_base"):
        self.base_path = Path(base_path)
        self.rules_path = self.base_path / "rules"
        self.patterns_path = self.base_path / "patterns"
        self.case_study_path = self.base_path / "case_study"
        
    def find_relevant_knowledge(
        self, 
        query: str, 
        categories: Optional[List[str]] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        根据查询检索相关知识
        
        Args:
            query: 查询字符串（用户问题或AI推理上下文）
            categories: 指定类别 ["rules", "patterns", "case_study"]，None 表示全部
            max_results: 每个类别最多返回结果数
            
        Returns:
            {
                "rules": [...],
                "patterns": [...],
                "case_study": [...],
                "summary": "找到 X 条规则、Y 条模式、Z 个案例"
            }
        """
        if categories is None:
            categories = ["rules", "patterns", "case_study"]
        
        results = {
            "rules": [],
            "patterns": [],
            "case_study": [],
            "summary": ""
        }
        
        # 提取关键词
        keywords = self._extract_keywords(query)
        
        # 检索各层知识库
        if "rules" in categories:
            results["rules"] = self._search_rules(keywords, max_results)
        
        if "patterns" in categories:
            results["patterns"] = self._search_patterns(keywords, max_results)
        
        if "case_study" in categories:
            results["case_study"] = self._search_case_study(keywords, max_results)
        
        # 生成摘要
        results["summary"] = f"找到 {len(results['rules'])} 条规则、{len(results['patterns'])} 条模式、{len(results['case_study'])} 个案例"
        
        return results
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        从查询中提取关键词
        """
        # 命理领域关键词库
        keyword_patterns = {
            "八字": ["八字", "四柱", "天干", "地支", "日主", "格局"],
            "紫微": ["紫微", "斗数", "命宫", "财帛宫", "夫妻宫", "事业宫"],
            "婚姻": ["婚姻", "感情", "夫妻", "配偶", "结婚", "离婚"],
            "财运": ["财运", "财富", "收入", "破财", "财帛"],
            "事业": ["事业", "工作", "职业", "升职", "创业"],
            "健康": ["健康", "疾病", "身体", "伤灾"],
            "时间": ["流年", "大运", "流月", "时辰", "年份"]
        }
        
        detected_keywords = []
        query_lower = query.lower()
        
        for category, patterns in keyword_patterns.items():
            for pattern in patterns:
                if pattern in query_lower or pattern in query:
                    detected_keywords.append(pattern)
        
        # 如果没有检测到关键词，提取中文词汇
        if not detected_keywords:
            chinese_words = re.findall(r'[\u4e00-\u9fff]+', query)
            detected_keywords = [w for w in chinese_words if len(w) >= 2][:5]
        
        return list(set(detected_keywords))
    
    def _search_rules(self, keywords: List[str], max_results: int) -> List[Dict]:
        """
        检索规则层（Markdown 文件）
        """
        results = []
        
        if not self.rules_path.exists():
            return results
        
        for rule_file in self.rules_path.glob("*.md"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 计算匹配分数
                score = self._calculate_match_score(content, keywords)
                
                if score > 0:
                    # 提取相关段落
                    relevant_sections = self._extract_relevant_sections(content, keywords)
                    
                    results.append({
                        "source": rule_file.name,
                        "type": "rule",
                        "score": score,
                        "content": relevant_sections[:500],  # 限制长度
                        "matched_keywords": [k for k in keywords if k in content]
                    })
            except Exception as e:
                print(f"⚠️ 读取规则文件失败 {rule_file}: {e}")
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def _search_patterns(self, keywords: List[str], max_results: int) -> List[Dict]:
        """
        检索模式层（JSON 文件）
        """
        results = []
        
        if not self.patterns_path.exists():
            return results
        
        for pattern_file in self.patterns_path.glob("*.json"):
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 将 JSON 转为文本进行匹配
                text_content = json.dumps(data, ensure_ascii=False)
                score = self._calculate_match_score(text_content, keywords)
                
                if score > 0:
                    results.append({
                        "source": pattern_file.name,
                        "type": "pattern",
                        "score": score,
                        "content": data,
                        "matched_keywords": [k for k in keywords if k in text_content]
                    })
            except Exception as e:
                print(f"⚠️ 读取模式文件失败 {pattern_file}: {e}")
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def _search_case_study(self, keywords: List[str], max_results: int) -> List[Dict]:
        """
        检索案例层（JSON 文件）
        """
        results = []
        
        if not self.case_study_path.exists():
            return results
        
        for case_file in self.case_study_path.glob("*.json"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                text_content = json.dumps(data, ensure_ascii=False)
                score = self._calculate_match_score(text_content, keywords)
                
                if score > 0:
                    results.append({
                        "source": case_file.name,
                        "type": "case_study",
                        "score": score,
                        "content": data,
                        "matched_keywords": [k for k in keywords if k in text_content]
                    })
            except Exception as e:
                print(f"⚠️ 读取案例文件失败 {case_file}: {e}")
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def _calculate_match_score(self, content: str, keywords: List[str]) -> float:
        """
        计算匹配分数（简单关键词频率）
        """
        content_lower = content.lower()
        score = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # 完整匹配得分更高
            if keyword in content:
                score += content.count(keyword) * 2.0
            # 部分匹配
            elif keyword_lower in content_lower:
                score += content_lower.count(keyword_lower) * 1.0
        
        return score
    
    def _extract_relevant_sections(self, content: str, keywords: List[str], context_size: int = 200) -> str:
        """
        提取相关段落（包含关键词的上下文）
        """
        sections = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in keywords):
                # 提取上下文
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                section = '\n'.join(lines[start:end])
                sections.append(section)
        
        return '\n---\n'.join(sections[:3]) if sections else content[:context_size]
    
    def get_stats(self) -> Dict[str, int]:
        """
        获取知识库统计信息
        """
        return {
            "rules_count": len(list(self.rules_path.glob("*.md"))) if self.rules_path.exists() else 0,
            "patterns_count": len(list(self.patterns_path.glob("*.json"))) if self.patterns_path.exists() else 0,
            "case_study_count": len(list(self.case_study_path.glob("*.json"))) if self.case_study_path.exists() else 0
        }


# 全局单例
_retrieval_router = None

def get_retrieval_router() -> RetrievalRouter:
    """获取全局检索路由器实例"""
    global _retrieval_router
    if _retrieval_router is None:
        _retrieval_router = RetrievalRouter()
    return _retrieval_router


def find_relevant_knowledge(query: str, categories: Optional[List[str]] = None, max_results: int = 5) -> Dict[str, Any]:
    """
    便捷函数：查询知识库
    供 AI prompts 调用
    """
    router = get_retrieval_router()
    return router.find_relevant_knowledge(query, categories, max_results)
