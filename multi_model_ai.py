"""
多模型 AI 调用模块
支持 ChatGPT、Gemini、ChatGLM、DeepSeek 等多个 AI 提供商
自动 fallback 机制确保高可用性
集成性能监控和使用统计
"""

import os
import json
import time
import httpx
from typing import Optional, List, Dict, Tuple

try:
    from ai_usage_logger import log_ai_usage
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    print("⚠️ ai_usage_logger 未找到，性能监控将不可用")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GLM_API_KEY = os.getenv("GLM_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


class MultiModelAI:
    """统一的多模型 AI 调用接口"""
    
    DEFAULT_SYSTEM_PROMPT = "你是 Lynker Master AI，擅长命理、八字、紫微斗数与铁板神数。请用中文回答问题。"
    
    FALLBACK_ORDER = ["chatgpt", "gemini", "glm", "deepseek"]
    
    @staticmethod
    def call_openai(prompt: str, system_prompt: str = None, model: str = "gpt-4o") -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """调用 OpenAI ChatGPT API"""
        if not OPENAI_AVAILABLE:
            return None, "OpenAI 库未安装", None
        if not OPENAI_API_KEY:
            return None, "缺少 OPENAI_API_KEY", None
        
        try:
            client = OpenAI(api_key=OPENAI_API_KEY)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.6,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content.strip()
            
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return answer, None, token_usage
            
        except Exception as e:
            error_msg = f"OpenAI 调用失败: {str(e)}"
            print(f"⚠️ {error_msg}")
            return None, error_msg, None
    
    @staticmethod
    def call_gemini(prompt: str, system_prompt: str = None, model: str = "gemini-1.5-pro") -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """调用 Google Gemini API"""
        if not GEMINI_AVAILABLE:
            return None, "Gemini 库未安装", None
        if not GEMINI_API_KEY:
            return None, "缺少 GEMINI_API_KEY", None
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(full_prompt)
            
            answer = response.text.strip()
            
            token_usage = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_usage = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
            
            return answer, None, token_usage
            
        except Exception as e:
            error_msg = f"Gemini 调用失败: {str(e)}"
            print(f"⚠️ {error_msg}")
            return None, error_msg, None
    
    @staticmethod
    def call_glm(prompt: str, system_prompt: str = None, model: str = "glm-4") -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """调用智谱 ChatGLM API"""
        if not GLM_API_KEY:
            return None, "缺少 GLM_API_KEY", None
        
        try:
            headers = {
                "Authorization": f"Bearer {GLM_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.6
            }
            
            response = httpx.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"].strip()
                
                token_usage = None
                if "usage" in data:
                    token_usage = {
                        "prompt_tokens": data["usage"].get("prompt_tokens"),
                        "completion_tokens": data["usage"].get("completion_tokens"),
                        "total_tokens": data["usage"].get("total_tokens")
                    }
                
                return answer, None, token_usage
            else:
                error_msg = f"GLM API 返回错误: {response.status_code} - {response.text}"
                print(f"⚠️ {error_msg}")
                return None, error_msg, None
                
        except Exception as e:
            error_msg = f"GLM 调用失败: {str(e)}"
            print(f"⚠️ {error_msg}")
            return None, error_msg, None
    
    @staticmethod
    def call_deepseek(prompt: str, system_prompt: str = None, model: str = "deepseek-chat") -> Tuple[Optional[str], Optional[str], Optional[Dict]]:
        """调用 DeepSeek API"""
        if not DEEPSEEK_API_KEY:
            return None, "缺少 DEEPSEEK_API_KEY", None
        
        try:
            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.6
            }
            
            response = httpx.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["choices"][0]["message"]["content"].strip()
                
                token_usage = None
                if "usage" in data:
                    token_usage = {
                        "prompt_tokens": data["usage"].get("prompt_tokens"),
                        "completion_tokens": data["usage"].get("completion_tokens"),
                        "total_tokens": data["usage"].get("total_tokens")
                    }
                
                return answer, None, token_usage
            else:
                error_msg = f"DeepSeek API 返回错误: {response.status_code} - {response.text}"
                print(f"⚠️ {error_msg}")
                return None, error_msg, None
                
        except Exception as e:
            error_msg = f"DeepSeek 调用失败: {str(e)}"
            print(f"⚠️ {error_msg}")
            return None, error_msg, None
    
    @classmethod
    def call(cls, provider: str, prompt: str, system_prompt: str = None, enable_fallback: bool = True) -> Dict:
        """
        统一的多模型调用接口（集成性能监控）
        
        Args:
            provider: 模型提供商 (chatgpt/gemini/glm/deepseek)
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            enable_fallback: 是否启用自动 fallback
        
        Returns:
            {
                "success": bool,
                "provider": str,
                "answer": str,
                "error": str,
                "fallback_used": bool,
                "latency": float
            }
        """
        provider = (provider or "chatgpt").lower()
        system_prompt = system_prompt or cls.DEFAULT_SYSTEM_PROMPT
        
        provider_map = {
            "chatgpt": cls.call_openai,
            "gpt": cls.call_openai,
            "openai": cls.call_openai,
            "gemini": cls.call_gemini,
            "google": cls.call_gemini,
            "glm": cls.call_glm,
            "chatglm": cls.call_glm,
            "zhipu": cls.call_glm,
            "deepseek": cls.call_deepseek,
            "ds": cls.call_deepseek
        }
        
        normalized_provider = provider
        if provider not in provider_map:
            normalized_provider = "chatgpt"
        
        start_time = time.time()
        answer, error, token_usage = provider_map[normalized_provider](prompt, system_prompt)
        latency = time.time() - start_time
        
        if answer:
            if LOGGER_AVAILABLE:
                log_ai_usage(normalized_provider, prompt, token_usage, latency, True, None, False)
            
            return {
                "success": True,
                "provider": normalized_provider,
                "answer": answer,
                "error": None,
                "fallback_used": False,
                "latency": round(latency, 3)
            }
        
        if LOGGER_AVAILABLE:
            log_ai_usage(normalized_provider, prompt, token_usage, latency, False, error, False)
        
        if not enable_fallback:
            return {
                "success": False,
                "provider": normalized_provider,
                "answer": None,
                "error": error,
                "fallback_used": False,
                "latency": round(latency, 3)
            }
        
        print(f"🔄 {normalized_provider} 失败，尝试 fallback...")
        
        for fallback_provider in cls.FALLBACK_ORDER:
            if fallback_provider == normalized_provider:
                continue
            
            if fallback_provider in provider_map:
                start_time = time.time()
                answer, error, token_usage = provider_map[fallback_provider](prompt, system_prompt)
                fallback_latency = time.time() - start_time
                
                if answer:
                    print(f"✅ Fallback 成功，使用 {fallback_provider}")
                    
                    if LOGGER_AVAILABLE:
                        log_ai_usage(fallback_provider, prompt, token_usage, fallback_latency, True, None, True)
                    
                    return {
                        "success": True,
                        "provider": fallback_provider,
                        "answer": answer,
                        "error": None,
                        "fallback_used": True,
                        "latency": round(fallback_latency, 3)
                    }
                else:
                    if LOGGER_AVAILABLE:
                        log_ai_usage(fallback_provider, prompt, token_usage, fallback_latency, False, error, True)
        
        total_latency = time.time() - start_time
        return {
            "success": False,
            "provider": normalized_provider,
            "answer": None,
            "error": "所有模型均未响应",
            "fallback_used": True,
            "latency": round(total_latency, 3)
        }
    
    @classmethod
    def get_available_providers(cls) -> List[Dict]:
        """获取所有可用的模型提供商"""
        providers = []
        
        if OPENAI_API_KEY and OPENAI_AVAILABLE:
            providers.append({"id": "chatgpt", "name": "ChatGPT (OpenAI)", "available": True})
        else:
            providers.append({"id": "chatgpt", "name": "ChatGPT (OpenAI)", "available": False})
        
        if GEMINI_API_KEY and GEMINI_AVAILABLE:
            providers.append({"id": "gemini", "name": "Gemini (Google)", "available": True})
        else:
            providers.append({"id": "gemini", "name": "Gemini (Google)", "available": False})
        
        if GLM_API_KEY:
            providers.append({"id": "glm", "name": "ChatGLM (智谱AI)", "available": True})
        else:
            providers.append({"id": "glm", "name": "ChatGLM (智谱AI)", "available": False})
        
        if DEEPSEEK_API_KEY:
            providers.append({"id": "deepseek", "name": "DeepSeek", "available": True})
        else:
            providers.append({"id": "deepseek", "name": "DeepSeek", "available": False})
        
        return providers


if __name__ == "__main__":
    print("🔍 检查可用的 AI 模型提供商：\n")
    providers = MultiModelAI.get_available_providers()
    for p in providers:
        status = "✅" if p["available"] else "❌"
        print(f"{status} {p['name']}")
    
    print("\n" + "="*60)
    print("测试调用（如果有可用的 API Key）:\n")
    
    test_prompt = "用一句话解释什么是八字命理学？"
    result = MultiModelAI.call("chatgpt", test_prompt, enable_fallback=True)
    
    if result["success"]:
        print(f"✅ 调用成功")
        print(f"📍 使用模型: {result['provider']}")
        print(f"🔄 Fallback: {result['fallback_used']}")
        print(f"💬 回答: {result['answer'][:100]}...")
    else:
        print(f"❌ 调用失败: {result['error']}")
