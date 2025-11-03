# -*- coding: utf-8 -*-
"""
🔧 LynkerAI 真命盘验证系统 - Vision Agent 更新任务
目标：创建/替换 verify/bazi_vision_agent.py 为 GPT-4o 专用版
"""

import os
import base64
import json
import requests
from datetime import datetime

class BaziVisionAgent:
    """
    LynkerAI 真命盘验证系统 v1.2
    三层架构：
      Layer1  VisionAgent  -> 调用 GPT-4o 识别命盘表格
      Layer2  Normalizer   -> 标准化为 JSON
      Layer3  Formatter    -> 整理输出供前端显示
    """

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY") or ""
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o"  # 或 gpt-4o-mini

    # ---------- Layer 1 ----------
    def process_image(self, image_base64, progress_callback=None):
        """主入口：识别命盘图片并输出标准化结果"""
        def say(msg): 
            if progress_callback: progress_callback(msg)

        say("🎯 启动 GPT-4o Vision 识别流程...")
        try:
            response = self._call_gpt4o_vision(image_base64)
            say("✅ 模型响应成功，开始标准化数据...")
            result = self._normalize_output(response)
            say("✅ 三层识别完成！")
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ---------- Layer 1 detail ----------
    def _call_gpt4o_vision(self, image_base64):
        """调用 GPT-4o Vision 并返回原始 JSON"""
        prompt = """
你是八字命盘识别专家，请从命盘图片中识别以下10行完整信息：

主星、天干、地支、藏干、副星、星运、自坐、空亡、纳音、神煞。
以标准JSON输出：

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
不要输出解释文字。
"""

        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2500
        }
        res = requests.post(self.endpoint, headers=headers, json=data, timeout=90)
        res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        return content

    # ---------- Layer 2 ----------
    def _normalize_output(self, response_text):
        """解析 GPT 输出为标准 JSON 结构"""
        try:
            json_text = self._extract_json_block(response_text)
            data = json.loads(json_text)
        except Exception as e:
            raise Exception(f"无法解析GPT输出: {str(e)}")

        rows = data.get("rows", {})
        # 自动补空值防止前端报错
        for key in ["主星","天干","地支","藏干","副星","星运","自坐","空亡","纳音","神煞"]:
            if key not in rows:
                rows[key] = ["", "", "", ""]

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "bazi": {
                "year_pillar": rows["天干"][0] + rows["地支"][0],
                "month_pillar": rows["天干"][1] + rows["地支"][1],
                "day_pillar": rows["天干"][2] + rows["地支"][2],
                "hour_pillar": rows["天干"][3] + rows["地支"][3]
            },
            "full_table": data
        }

    # ---------- Layer 3 ----------
    def _extract_json_block(self, text):
        """提取 JSON 部分"""
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("未找到 JSON 区块")
        return text[start:end+1]
