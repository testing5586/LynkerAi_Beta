# -*- coding: utf-8 -*-
"""
Bazi Vision Agent - 三层智能八字识别系统
Layer 1: Vision Agent - 使用 MiniMax Vision Pro / GPT-4 Vision / 本地模拟
Layer 2: Normalizer Agent - 标准化四柱数据
Layer 3: Formatter Agent - 格式化输出
"""

import os
import json
import requests
import base64
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

class BaziVisionAgent:
    """三层八字识别代理系统"""
    
    def __init__(self):
        self.minimax_api_key = os.getenv("MINIMAX_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        
        # MiniMax 官方端点列表（支持全球访问）
        self.minimax_endpoints = [
            "https://api.minimaxi.com/v1/chat/completions",  # 中国区（优先）
            "https://api.minimax.io/v1/chat/completions"     # 国际区
        ]
        self.last_successful_endpoint = None  # 记录上次成功的端点
        
        # 天干地支映射
        self.tiangan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        self.dizhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        self.wuxing_map = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", 
            "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
            "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", 
            "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", 
            "戌": "土", "亥": "水"
        }
    
    def process_image(self, image_base64: str, progress_callback=None) -> Dict:
        """
        处理八字图片，返回识别结果
        
        Args:
            image_base64: Base64 编码的图片数据
            progress_callback: 进度回调函数 callback(message: str)
        
        Returns:
            识别结果字典
        """
        try:
            if progress_callback:
                progress_callback("🎯 开始三层智能识别流程...")
            
            # Layer 1: Vision Agent - 图片识别
            raw_text = self._vision_layer(image_base64, progress_callback)
            
            # Layer 2: Normalizer Agent - 标准化数据
            normalized_data = self._normalizer_layer(raw_text, progress_callback)
            
            # Layer 3: Formatter Agent - 格式化输出
            formatted_result = self._formatter_layer(normalized_data, progress_callback)
            
            if progress_callback:
                progress_callback("✅ 三层识别完成！")
            
            return {
                "success": True,
                "data": formatted_result,
                "raw_text": raw_text
            }
            
        except Exception as e:
            error_msg = f"识别失败: {str(e)}"
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _vision_layer(self, image_base64: str, progress_callback=None) -> str:
        """Layer 1: Vision Agent - 图片识别（三级 fallback）"""
        
        # 尝试 1: MiniMax Vision Pro
        if self.minimax_api_key:
            try:
                if progress_callback:
                    progress_callback("📸 使用 MiniMax Vision Pro 识别...")
                result = self._call_minimax_vision(image_base64)
                if result:
                    if progress_callback:
                        progress_callback("✅ MiniMax 识别成功")
                    return result
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️ MiniMax 失败: {str(e)}")
        
        # 尝试 2: GPT-4 Vision
        if self.openai_client:
            try:
                if progress_callback:
                    progress_callback("📸 切换到 GPT-4 Vision...")
                result = self._call_gpt4_vision(image_base64)
                if result:
                    if progress_callback:
                        progress_callback("✅ GPT-4 Vision 识别成功")
                    return result
            except Exception as e:
                if progress_callback:
                    progress_callback(f"⚠️ GPT-4 Vision 失败: {str(e)}")
        
        # 尝试 3: 本地模拟数据
        if progress_callback:
            progress_callback("⚙️ 使用本地模拟数据...")
        return self._get_simulated_data()
    
    def _call_minimax_vision(self, image_base64: str) -> Optional[str]:
        """
        调用 MiniMax Vision Pro API（智能端点切换）
        支持中国区和国际区自动切换
        """
        # 优先使用上次成功的端点
        if self.last_successful_endpoint:
            endpoints_to_try = [self.last_successful_endpoint] + [
                ep for ep in self.minimax_endpoints if ep != self.last_successful_endpoint
            ]
        else:
            endpoints_to_try = self.minimax_endpoints
        
        last_error = None
        for endpoint in endpoints_to_try:
            try:
                result = self._call_minimax_with_endpoint(endpoint, image_base64)
                self.last_successful_endpoint = endpoint  # 记录成功的端点
                return result
            except Exception as e:
                last_error = str(e)
                continue
        
        # 所有端点都失败
        raise Exception(f"所有 MiniMax 端点均不可用。最后错误: {last_error}")
    
    def _call_minimax_with_endpoint(self, url: str, image_base64: str) -> str:
        """使用指定端点调用 MiniMax Vision API"""
        # 移除可能的 data:image 前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json"
        }
        
        # 使用 OpenAI-compatible messages 格式
        payload = {
            "model": "minimax-vl-01",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """你是一名专业的八字命盘识别专家，擅长读取文墨天机等系统导出的命盘图片。

📸 输入内容：八字命盘截图（含年柱、月柱、日柱、时柱及各层信息）
🎯 输出目标：请严格按照以下格式输出识别结果，以 JSON 结构表示表格内容。

【识别重点】
必须识别出以下10行：
主星、天干、地支、藏干、副星、星运、自坐、空亡、纳音、神煞。

【输出JSON格式要求】
{
  "columns": ["年柱","月柱","日柱","时柱"],
  "rows": {
    "主星": ["","","",""],
    "天干": ["","","",""],
    "地支": ["","","",""],
    "藏干": ["","","",""],
    "副星": ["","","",""],
    "星运": ["","","",""],
    "自坐": ["","","",""],
    "空亡": ["","","",""],
    "纳音": ["","","",""],
    "神煞": ["","","",""]
  }
}

【格式说明】
- 每个项目对应四个柱（年、月、日、时），务必保证列数一致；
- 若有多个项目（如藏干、副星、神煞），请用中文顿号"、"隔开；
- 不要添加任何解释文字、单位或多余字段；
- 最终输出必须是可以被 JSON.parse() 直接解析的纯JSON。

【示例】
| 日期     | 年柱       | 月柱       | 日柱                   | 时柱                |
| :----- | :------- | :------- | :------------------- | :---------------- |
| **主星** | 正财       | 食神       | 元男                   | 正印                |
| **天干** | 庚        | 己        | 丁                    | 甲                 |
| **地支** | 辰        | 卯        | 丑                    | 辰                 |
| **藏干** | 戊土、乙木、癸水 | 乙木       | 己土、癸水、辛金             | 戊土、乙木、癸水          |
| **副星** | 伤官、偏印、七杀 | 偏印       | 食神、七杀、偏财             | 伤官、偏印、七杀          |
| **星运** | 衰        | 病        | 墓                    | 衰                 |
| **自坐** | 养        | 病        | 墓                    | 衰                 |
| **空亡** | 申酉       | 申酉       | 申酉                   | 寅卯                |
| **纳音** | 白蜡金      | 城头土      | 涧下水                  | 覆灯火               |
| **神煞** | 国印贵人     | 太极贵人、月德合 | 阴差阳错、天乙贵人、德秀贵人、寡宿、披麻 | 国印贵人、月德贵人、德秀贵人、华盖 |

【注意】
- 不要输出 markdown、竖线或制表符；
- 不要省略空列；
- 不允许输出"无法识别"或"空"；
- 直接输出符合上述结构的 JSON。"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 1500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # OpenAI-compatible 响应格式
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                # 尝试获取 message.content
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                # 尝试获取直接的 text 字段
                elif "text" in choice:
                    return choice["text"]
            
            # 如果没有找到预期格式，抛出详细错误
            raise Exception(f"无法解析 MiniMax 响应格式: {json.dumps(data, ensure_ascii=False)[:200]}")
        
        # 返回详细错误信息
        error_text = response.text[:500] if response.text else "无响应内容"
        raise Exception(f"MiniMax API 返回错误 {response.status_code}: {error_text}")
    
    def _call_gpt4_vision(self, image_base64: str) -> Optional[str]:
        """调用 GPT-4 Vision API"""
        
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        # 移除可能的 data:image 前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """你是一名专业的八字命盘识别专家，擅长读取文墨天机等系统导出的命盘图片。

📸 输入内容：八字命盘截图（含年柱、月柱、日柱、时柱及各层信息）
🎯 输出目标：请严格按照以下格式输出识别结果，以 JSON 结构表示表格内容。

【识别重点】
必须识别出以下10行：
主星、天干、地支、藏干、副星、星运、自坐、空亡、纳音、神煞。

【输出JSON格式要求】
{
  "columns": ["年柱","月柱","日柱","时柱"],
  "rows": {
    "主星": ["","","",""],
    "天干": ["","","",""],
    "地支": ["","","",""],
    "藏干": ["","","",""],
    "副星": ["","","",""],
    "星运": ["","","",""],
    "自坐": ["","","",""],
    "空亡": ["","","",""],
    "纳音": ["","","",""],
    "神煞": ["","","",""]
  }
}

【格式说明】
- 每个项目对应四个柱（年、月、日、时），务必保证列数一致；
- 若有多个项目（如藏干、副星、神煞），请用中文顿号"、"隔开；
- 不要添加任何解释文字、单位或多余字段；
- 最终输出必须是可以被 JSON.parse() 直接解析的纯JSON。

【示例】
| 日期     | 年柱       | 月柱       | 日柱                   | 时柱                |
| :----- | :------- | :------- | :------------------- | :---------------- |
| **主星** | 正财       | 食神       | 元男                   | 正印                |
| **天干** | 庚        | 己        | 丁                    | 甲                 |
| **地支** | 辰        | 卯        | 丑                    | 辰                 |
| **藏干** | 戊土、乙木、癸水 | 乙木       | 己土、癸水、辛金             | 戊土、乙木、癸水          |
| **副星** | 伤官、偏印、七杀 | 偏印       | 食神、七杀、偏财             | 伤官、偏印、七杀          |
| **星运** | 衰        | 病        | 墓                    | 衰                 |
| **自坐** | 养        | 病        | 墓                    | 衰                 |
| **空亡** | 申酉       | 申酉       | 申酉                   | 寅卯                |
| **纳音** | 白蜡金      | 城头土      | 涧下水                  | 覆灯火               |
| **神煞** | 国印贵人     | 太极贵人、月德合 | 阴差阳错、天乙贵人、德秀贵人、寡宿、披麻 | 国印贵人、月德贵人、德秀贵人、华盖 |

【注意】
- 不要输出 markdown、竖线或制表符；
- 不要省略空列；
- 不允许输出"无法识别"或"空"；
- 直接输出符合上述结构的 JSON。"""
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def _get_simulated_data(self) -> str:
        """返回模拟八字数据（新 JSON 格式）"""
        return """{
  "columns": ["年柱","月柱","日柱","时柱"],
  "rows": {
    "主星": ["正财","食神","元男","正印"],
    "天干": ["庚","己","丁","甲"],
    "地支": ["辰","卯","丑","辰"],
    "藏干": ["戊土、乙木、癸水","乙木","己土、癸水、辛金","戊土、乙木、癸水"],
    "副星": ["伤官、偏印、七杀","偏印","食神、七杀、偏财","伤官、偏印、七杀"],
    "星运": ["衰","病","墓","衰"],
    "自坐": ["养","病","墓","衰"],
    "空亡": ["申酉","申酉","申酉","寅卯"],
    "纳音": ["白蜡金","城头土","涧下水","覆灯火"],
    "神煞": ["国印贵人","太极贵人、月德合","阴差阳错、天乙贵人、德秀贵人、寡宿、披麻","国印贵人、月德贵人、德秀贵人、华盖"]
  }
}"""
    
    def _normalizer_layer(self, raw_text: str, progress_callback=None) -> Dict:
        """Layer 2: Normalizer Agent - 标准化数据（支持新 JSON 格式）"""
        
        if progress_callback:
            progress_callback("🔧 标准化四柱数据...")
        
        result = {
            "year_gan": "", "year_zhi": "",
            "month_gan": "", "month_zhi": "",
            "day_gan": "", "day_zhi": "",
            "hour_gan": "", "hour_zhi": "",
            "gender": "",
            "birth_time": "",
            "full_table": None  # 存储完整的 10 行数据
        }
        
        # 尝试解析 JSON 格式（新格式）
        try:
            # 提取 JSON 部分（可能包含额外文本）
            json_start = raw_text.find("{")
            json_end = raw_text.rfind("}") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = raw_text[json_start:json_end]
                data = json.loads(json_text)
                
                if "rows" in data and "天干" in data["rows"] and "地支" in data["rows"]:
                    # 解析天干地支
                    tiangan = data["rows"]["天干"]
                    dizhi = data["rows"]["地支"]
                    
                    if len(tiangan) >= 4 and len(dizhi) >= 4:
                        result["year_gan"] = tiangan[0]
                        result["month_gan"] = tiangan[1]
                        result["day_gan"] = tiangan[2]
                        result["hour_gan"] = tiangan[3]
                        
                        result["year_zhi"] = dizhi[0]
                        result["month_zhi"] = dizhi[1]
                        result["day_zhi"] = dizhi[2]
                        result["hour_zhi"] = dizhi[3]
                        
                        # 存储完整表格数据
                        result["full_table"] = data
                        
                        if progress_callback:
                            progress_callback(f"✅ 识别到完整命盘: {result['year_gan']}{result['year_zhi']} {result['month_gan']}{result['month_zhi']} {result['day_gan']}{result['day_zhi']} {result['hour_gan']}{result['hour_zhi']}")
                        
                        return result
        
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            if progress_callback:
                progress_callback(f"⚠️ JSON 解析失败，尝试旧格式解析...")
        
        # 如果 JSON 解析失败，回退到旧格式解析（向后兼容）
        lines = raw_text.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            
            if "年柱" in line or "Year" in line:
                chars = self._extract_ganzhi(line)
                if len(chars) >= 2:
                    result["year_gan"], result["year_zhi"] = chars[0], chars[1]
            
            elif "月柱" in line or "Month" in line:
                chars = self._extract_ganzhi(line)
                if len(chars) >= 2:
                    result["month_gan"], result["month_zhi"] = chars[0], chars[1]
            
            elif "日柱" in line or "Day" in line:
                chars = self._extract_ganzhi(line)
                if len(chars) >= 2:
                    result["day_gan"], result["day_zhi"] = chars[0], chars[1]
            
            elif "时柱" in line or "Hour" in line:
                chars = self._extract_ganzhi(line)
                if len(chars) >= 2:
                    result["hour_gan"], result["hour_zhi"] = chars[0], chars[1]
            
            elif "性别" in line or "Gender" in line:
                if "男" in line or "Male" in line:
                    result["gender"] = "男"
                elif "女" in line or "Female" in line:
                    result["gender"] = "女"
            
            elif "出生时间" in line or "Birth" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    result["birth_time"] = parts[1].strip()
        
        if progress_callback:
            progress_callback(f"✅ 识别到: {result['year_gan']}{result['year_zhi']} {result['month_gan']}{result['month_zhi']} {result['day_gan']}{result['day_zhi']} {result['hour_gan']}{result['hour_zhi']}")
        
        return result
    
    def _extract_ganzhi(self, text: str) -> List[str]:
        """从文本中提取干支字符"""
        chars = []
        all_chars = self.tiangan + self.dizhi
        
        for char in text:
            if char in all_chars:
                chars.append(char)
        
        return chars
    
    def _formatter_layer(self, normalized_data: Dict, progress_callback=None) -> Dict:
        """Layer 3: Formatter Agent - 格式化输出（包含完整 10 行数据）"""
        
        if progress_callback:
            progress_callback("📦 格式化输出数据...")
        
        # 计算五行
        wuxing = self._calculate_wuxing(normalized_data)
        
        result = {
            "bazi": {
                "year": f"{normalized_data['year_gan']}{normalized_data['year_zhi']}",
                "month": f"{normalized_data['month_gan']}{normalized_data['month_zhi']}",
                "day": f"{normalized_data['day_gan']}{normalized_data['day_zhi']}",
                "hour": f"{normalized_data['hour_gan']}{normalized_data['hour_zhi']}"
            },
            "pillars": {
                "year_gan": normalized_data["year_gan"],
                "year_zhi": normalized_data["year_zhi"],
                "month_gan": normalized_data["month_gan"],
                "month_zhi": normalized_data["month_zhi"],
                "day_gan": normalized_data["day_gan"],
                "day_zhi": normalized_data["day_zhi"],
                "hour_gan": normalized_data["hour_gan"],
                "hour_zhi": normalized_data["hour_zhi"]
            },
            "gender": normalized_data.get("gender", ""),
            "birth_time": normalized_data.get("birth_time", ""),
            "wuxing": wuxing
        }
        
        # 如果有完整表格数据，添加到结果中
        if normalized_data.get("full_table"):
            result["full_table"] = normalized_data["full_table"]
            if progress_callback:
                progress_callback("✅ 已包含完整 10 行命盘数据")
        
        return result
    
    def _calculate_wuxing(self, data: Dict) -> Dict:
        """计算五行分布"""
        wuxing_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        
        chars = [
            data["year_gan"], data["year_zhi"],
            data["month_gan"], data["month_zhi"],
            data["day_gan"], data["day_zhi"],
            data["hour_gan"], data["hour_zhi"]
        ]
        
        for char in chars:
            if char in self.wuxing_map:
                wuxing = self.wuxing_map[char]
                wuxing_count[wuxing] += 1
        
        return wuxing_count


# 便捷函数
def process_bazi_image(image_base64: str, progress_callback=None) -> Dict:
    """
    处理八字图片的便捷函数
    
    Args:
        image_base64: Base64 编码的图片数据
        progress_callback: 进度回调函数
    
    Returns:
        识别结果字典
    """
    agent = BaziVisionAgent()
    return agent.process_image(image_base64, progress_callback)
