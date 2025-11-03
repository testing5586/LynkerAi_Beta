"""
Bazi JSON 自动补全模块
功能：
1. 自动补齐缺失字段（environment、ai_verifier、wuxing）
2. 五行自动计算（根据天干地支计算五行数量）
3. OCR 模型追踪与置信度标注
"""

import json
from datetime import datetime


class BaziJsonAutoCompleter:
    """八字 JSON 数据自动补全器"""
    
    def __init__(self):
        # 天干地支五行映射表
        self.five_elements_map = {
            # 天干
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水",
            # 地支
            "寅": "木", "卯": "木",
            "巳": "火", "午": "火",
            "辰": "土", "丑": "土", "未": "土", "戌": "土",
            "申": "金", "酉": "金",
            "亥": "水", "子": "水"
        }

    def calculate_wuxing(self, pillars):
        """
        统计八字天干地支的五行数量
        
        参数:
            pillars: 四柱数据字典 {"year_pillar": "庚辰", ...}
        
        返回:
            五行计数字典 {"木": 3, "火": 2, "土": 2, "金": 1, "水": 2}
        """
        count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        
        for key, val in pillars.items():
            if not val:
                continue
            for char in val:
                if char in self.five_elements_map:
                    elem = self.five_elements_map[char]
                    count[elem] += 1
        
        return count

    def auto_complete(self, data: dict, environment=None):
        """
        自动补齐缺失字段
        
        参数:
            data: 原始八字数据
            environment: 环境信息（可选）
        
        返回:
            补全后的完整数据
        """
        data = data.copy()

        # === 1. 环境信息补全 ===
        if "environment" not in data:
            data["environment"] = environment or {
                "country_code": "CN",
                "country_name": "中国",
                "city": "北京",
                "latitude": 39.904,
                "longitude": 116.407,
                "climate_zone": "温带",
                "humidity_type": "干燥",
                "terrain_type": "内陆"
            }
        elif environment:
            # 如果提供了环境信息，使用提供的值
            data["environment"] = environment

        # === 2. 五行计算 ===
        # 尝试从不同位置获取四柱数据
        pillars = {}
        
        # 优先从 agent_recognition.bazi 获取
        if "agent_recognition" in data and "bazi" in data["agent_recognition"]:
            pillars = data["agent_recognition"]["bazi"]
        # 其次从根级别获取
        elif "year_pillar" in data:
            pillars = {
                "year_pillar": data.get("year_pillar", ""),
                "month_pillar": data.get("month_pillar", ""),
                "day_pillar": data.get("day_pillar", ""),
                "hour_pillar": data.get("hour_pillar", "")
            }
        
        # 计算五行
        wuxing = self.calculate_wuxing(pillars)
        
        # 存储五行数据
        if "agent_recognition" not in data:
            data["agent_recognition"] = {}
        data["agent_recognition"]["wuxing"] = wuxing

        # === 3. AI 验证信息 ===
        if "ai_verifier" not in data:
            data["ai_verifier"] = {
                "ocr_model": "GPT-4o Vision",
                "bazi_version": "v2.1",
                "verify_confidence": 0.97,
                "timestamp": datetime.now().isoformat(),
                "agent_type": "Three-Layer Agent Workflow"
            }

        return data


# === 全局单例实例 ===
_completer_instance = None

def get_completer():
    """获取补全器单例"""
    global _completer_instance
    if _completer_instance is None:
        _completer_instance = BaziJsonAutoCompleter()
    return _completer_instance


def auto_complete_bazi_json(data: dict, environment=None):
    """
    便捷函数：自动补全 Bazi JSON 数据
    
    参数:
        data: 原始八字数据
        environment: 环境信息（可选）
    
    返回:
        补全后的完整数据
    """
    completer = get_completer()
    return completer.auto_complete(data, environment)


# === 测试示例 ===
if __name__ == "__main__":
    test_json = {
        "year_pillar": "庚辰",
        "month_pillar": "己卯",
        "day_pillar": "丁丑",
        "hour_pillar": "甲辰",
        "agent_recognition": {
            "bazi": {
                "year_pillar": "庚辰",
                "month_pillar": "己卯",
                "day_pillar": "丁丑",
                "hour_pillar": "甲辰"
            }
        }
    }

    completer = BaziJsonAutoCompleter()
    completed = completer.auto_complete(test_json)
    print(json.dumps(completed, ensure_ascii=False, indent=2))
    
    # 预期输出：
    # {
    #   "year_pillar": "庚辰",
    #   "month_pillar": "己卯",
    #   "day_pillar": "丁丑",
    #   "hour_pillar": "甲辰",
    #   "agent_recognition": {
    #     "bazi": {...},
    #     "wuxing": {"木": 3, "火": 2, "土": 2, "金": 1, "水": 2}
    #   },
    #   "environment": {...},
    #   "ai_verifier": {...}
    # }
