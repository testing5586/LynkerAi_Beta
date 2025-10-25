"""
情绪识别器：优先 OpenAI，兜底离线词典
Emotion Analyzer: OpenAI (priority) + Offline Dictionary (fallback)
"""

import os
import re
from typing import Dict, Tuple

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 离线中文情绪词典
OFFLINE_EMOTION_DICT = {
    "positive": ["开心", "高兴", "快乐", "喜欢", "爱", "满意", "幸福", "希望", "感恩", "顺利"],
    "anxious": ["焦虑", "担心", "不安", "害怕", "恐惧", "紧张", "忧虑", "迷茫", "犹豫"],
    "sad": ["难过", "伤心", "痛苦", "悲伤", "失望", "沮丧", "孤独", "后悔", "遗憾"],
    "angry": ["生气", "愤怒", "讨厌", "恨", "不满", "烦躁", "厌烦", "抱怨"],
    "neutral": []  # 默认中性
}

class EmotionAnalyzer:
    """情绪分析器"""
    
    def __init__(self):
        self.openai_client = None
        self.mode = "offline"
        
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LYNKER_MASTER_KEY")
            if api_key:
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.mode = "openai"
                    print("✅ 情绪识别：使用 OpenAI 模式")
                except Exception as e:
                    print(f"⚠️ OpenAI 初始化失败，切换到离线模式: {e}")
        
        if self.mode == "offline":
            print("✅ 情绪识别：使用离线词典模式")
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        分析文本情绪
        
        Returns:
            (label, score): 例如 ("anxious", 0.75)
        """
        if not text or not text.strip():
            return ("neutral", 0.5)
        
        if self.mode == "openai" and self.openai_client:
            return self._analyze_with_openai(text)
        else:
            return self._analyze_with_dict(text)
    
    def _analyze_with_openai(self, text: str) -> Tuple[str, float]:
        """使用 OpenAI 分析情绪"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "system",
                    "content": "你是情绪分析专家。分析中文文本情绪，只返回 JSON 格式：{\"label\": \"positive/neutral/anxious/sad/angry\", \"score\": 0-1 之间的数值}"
                }, {
                    "role": "user",
                    "content": f"分析这段文本的情绪：{text[:200]}"
                }],
                temperature=0.3,
                max_tokens=50
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 提取 JSON
            import json
            result = json.loads(result_text)
            
            label = result.get("label", "neutral")
            score = float(result.get("score", 0.5))
            
            # 确保 label 有效
            valid_labels = ["positive", "neutral", "anxious", "sad", "angry"]
            if label not in valid_labels:
                label = "neutral"
            
            # 确保 score 在 0-1 之间
            score = max(0.0, min(1.0, score))
            
            return (label, score)
            
        except Exception as e:
            print(f"⚠️ OpenAI 情绪分析失败，切换到离线模式: {e}")
            return self._analyze_with_dict(text)
    
    def _analyze_with_dict(self, text: str) -> Tuple[str, float]:
        """使用离线词典分析情绪"""
        text_lower = text.lower()
        
        emotion_scores = {}
        
        for emotion, keywords in OFFLINE_EMOTION_DICT.items():
            if emotion == "neutral":
                continue
            
            count = sum(1 for keyword in keywords if keyword in text)
            if count > 0:
                emotion_scores[emotion] = count
        
        if not emotion_scores:
            return ("neutral", 0.5)
        
        # 找出最高分情绪
        top_emotion = max(emotion_scores, key=emotion_scores.get)
        max_count = emotion_scores[top_emotion]
        
        # 计算置信度（简化：关键词数 / 10，上限 0.9）
        score = min(0.9, max_count * 0.3 + 0.3)
        
        return (top_emotion, score)

# 全局单例
_analyzer = None

def get_analyzer() -> EmotionAnalyzer:
    """获取情绪分析器单例"""
    global _analyzer
    if _analyzer is None:
        _analyzer = EmotionAnalyzer()
    return _analyzer
