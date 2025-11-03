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
        """调用 MiniMax Vision Pro API"""
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        
        # 移除可能的 data:image 前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        
        headers = {
            "Authorization": f"Bearer {self.minimax_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "MiniMax-VL-01",
            "messages": [
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
                            "text": """请识别这张八字命盘图片，提取以下信息：

1. 四柱八字（年柱、月柱、日柱、时柱，每柱包含天干和地支）
2. 性别（男/女）
3. 出生日期和时间（如果图片中有显示）

请以以下格式输出：
年柱: [天干][地支]
月柱: [天干][地支]
日柱: [天干][地支]
时柱: [天干][地支]
性别: 男/女
出生时间: YYYY-MM-DD HH:MM（如果有）

只输出识别到的内容，不要添加额外说明。"""
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
        
        raise Exception(f"MiniMax API 返回错误: {response.status_code}")
    
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
                            "text": """请识别这张八字命盘图片，提取以下信息：

1. 四柱八字（年柱、月柱、日柱、时柱，每柱包含天干和地支）
2. 性别（男/女）
3. 出生日期和时间（如果图片中有显示）

请以以下格式输出：
年柱: [天干][地支]
月柱: [天干][地支]
日柱: [天干][地支]
时柱: [天干][地支]
性别: 男/女
出生时间: YYYY-MM-DD HH:MM（如果有）

只输出识别到的内容，不要添加额外说明。"""
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _get_simulated_data(self) -> str:
        """返回模拟八字数据"""
        return """年柱: 庚辰
月柱: 己卯
日柱: 甲子
时柱: 乙丑
性别: 男
出生时间: 2000-03-15 10:30"""
    
    def _normalizer_layer(self, raw_text: str, progress_callback=None) -> Dict:
        """Layer 2: Normalizer Agent - 标准化数据"""
        
        if progress_callback:
            progress_callback("🔧 标准化四柱数据...")
        
        result = {
            "year_gan": "", "year_zhi": "",
            "month_gan": "", "month_zhi": "",
            "day_gan": "", "day_zhi": "",
            "hour_gan": "", "hour_zhi": "",
            "gender": "",
            "birth_time": ""
        }
        
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
        """Layer 3: Formatter Agent - 格式化输出"""
        
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
