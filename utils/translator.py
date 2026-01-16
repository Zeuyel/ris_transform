"""
翻译服务
支持多种翻译API
"""
import requests
from typing import Optional, Literal
from enum import Enum


class TranslationService(str, Enum):
    """翻译服务枚举"""
    DEEPLX = "deeplx"
    MISSUO = "missuo"
    LINUXDO = "linuxdo"


class Translator:
    """翻译器"""
    
    def __init__(
        self,
        service: TranslationService = TranslationService.DEEPLX,
        api_token: Optional[str] = None
    ):
        """
        初始化翻译器
        
        Args:
            service: 翻译服务
            api_token: API令牌（某些服务需要）
        """
        self.service = service
        self.api_token = api_token
        
        # DeepLX API 端点
        self.deeplx_endpoints = [
            "https://api.deepl.com/v2/translate",
            "https://deeplx.mingming.dev/translate",
        ]
    
    def translate(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "ZH"
    ) -> Optional[str]:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言（auto为自动检测）
            target_lang: 目标语言
            
        Returns:
            翻译后的文本，失败返回 None
        """
        if not text or not text.strip():
            return None
        
        if self.service == TranslationService.DEEPLX:
            return self._translate_deeplx(text, source_lang, target_lang)
        elif self.service == TranslationService.MISSUO:
            return self._translate_missuo(text, source_lang, target_lang)
        elif self.service == TranslationService.LINUXDO:
            return self._translate_linuxdo(text, source_lang, target_lang)
        else:
            raise ValueError(f"不支持的翻译服务: {self.service}")
    
    def _translate_deeplx(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """使用 DeepLX 翻译"""
        for endpoint in self.deeplx_endpoints:
            try:
                payload = {
                    "text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang
                }
                
                response = requests.post(
                    endpoint,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("data", result.get("text"))
            
            except Exception as e:
                print(f"DeepLX 翻译失败 ({endpoint}): {e}")
                continue
        
        return None
    
    def _translate_missuo(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """使用 Missuo 翻译服务"""
        if not self.api_token:
            raise ValueError("Missuo 服务需要 API Token")
        
        try:
            endpoint = "https://api.missuo.me/translate"
            
            payload = {
                "text": text,
                "source": source_lang,
                "target": target_lang,
                "token": self.api_token
            }
            
            response = requests.post(endpoint, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("translation")
        
        except Exception as e:
            print(f"Missuo 翻译失败: {e}")
        
        return None
    
    def _translate_linuxdo(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> Optional[str]:
        """使用 LinuxDo 翻译服务"""
        if not self.api_token:
            raise ValueError("LinuxDo 服务需要 API Token")
        
        try:
            endpoint = "https://linux.do/api/translate"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            
            payload = {
                "text": text,
                "from": source_lang,
                "to": target_lang
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("translated_text")
        
        except Exception as e:
            print(f"LinuxDo 翻译失败: {e}")
        
        return None

