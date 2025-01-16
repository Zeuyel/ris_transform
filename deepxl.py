import requests
import json
import random
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote

class ServiceType(Enum):
    MISSUO = "missuo"
    LINUXDO = "linuxdo"
    FINDMYIP = "findmyip"
    EDU6 = "edu6"
    SMNET = "smnet"

@dataclass
class TranslationResult:
    text: str
    alternatives: List[str] = None
    source_lang: str = None
    target_lang: str = None

@dataclass
class TranslationService:
    name: ServiceType
    base_url: str
    token: Optional[str] = None
    weight: int = 1
    last_used: float = 0
    failure_count: int = 0
    max_failures: int = 3
    failure_cooldown: float = 20  # 失败后的冷却时间
    success_cooldown: float = 1   # 成功后的冷却时间
    method: str = "POST"
    request_timeout: float = 10  # 添加请求超时参数

    @property
    def url(self) -> str:
        """根据服务类型生成完整的URL"""
        if not self.token:
            return self.base_url
            
        if self.name == ServiceType.MISSUO:
            return f"{self.base_url}?key={self.token}"
        elif self.name == ServiceType.LINUXDO:
            return f"https://api.deeplx.org/{self.token}/translate"
        elif self.name == ServiceType.EDU6:
            return f"{self.base_url}?token={self.token}"
        return self.base_url

    def make_request(self, text: str, source_lang: str, target_lang: str) -> Optional[TranslationResult]:
        """执行翻译请求，带超时控制"""
        headers = {"Content-Type": "application/json"}
        
        try:
            if self.name == ServiceType.FINDMYIP:
                # GET请求，参数通过URL传递
                encoded_text = quote(text)
                url = f"{self.base_url}?text={encoded_text}&source_lang={source_lang}&target_lang={target_lang}"
                response = requests.get(url, timeout=self.request_timeout)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 200:
                        return TranslationResult(
                            text=result["data"]["translate_result"]
                        )
            else:
                # POST请求
                payload = {
                    "text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang
                }
                response = requests.post(self.url, headers=headers, json=payload, 
                                      timeout=self.request_timeout)
                if response.status_code == 200:
                    result = response.json()
                    if result.get("code") == 200:
                        if self.name == ServiceType.SMNET:
                            return TranslationResult(
                                text=result["data"],
                                alternatives=result.get("alternatives", []),
                                source_lang=result.get("source_lang"),
                                target_lang=result.get("target_lang")
                            )
                        else:
                            return TranslationResult(
                                text=result.get("data", "")
                            )
            return None
        except Exception as e:
            print(f"服务 {self.name.value} 请求失败: {str(e)}")
            return None

class TranslationLoadBalancer:
    def __init__(self):
        self.services: List[TranslationService] = []
        self.current_index = 0
    
    def add_service(self, service: TranslationService):
        """添加翻译服务"""
        self.services.append(service)
    
    def get_next_service(self) -> Optional[TranslationService]:
        """获取下一个可用的服务（带权重和故障处理）"""
        if not self.services:
            print("没有配置任何翻译服务")
            return None
            
        current_time = time.time()
        available_services = [
            service for service in self.services
            if (service.failure_count < service.max_failures and 
                current_time - service.last_used >= (
                    service.failure_cooldown if service.failure_count > 0 
                    else service.success_cooldown
                ))
        ]
        
        if not available_services:
            print(f"所有服务状态：")
            for service in self.services:
                cooldown = (service.failure_cooldown if service.failure_count > 0 
                           else service.success_cooldown)
                print(f"- {service.name.value}: 失败次数={service.failure_count}, "
                      f"冷却剩余时间={cooldown - (current_time - service.last_used):.1f}秒")
            return None
            
        weighted_pool = []
        for service in available_services:
            weighted_pool.extend([service] * service.weight)
            
        return random.choice(weighted_pool)
    
    def mark_failure(self, service: TranslationService):
        """标记服务失败"""
        service.failure_count += 1
        service.last_used = time.time()
    
    def mark_success(self, service: TranslationService):
        """标记服务成功"""
        service.failure_count = 0
        service.last_used = time.time()

def translate_text(text: str, source_lang: str = "auto", target_lang: str = "ZH", 
                  load_balancer: Optional[TranslationLoadBalancer] = None,
                  max_retries: int = 5,
                  timeout: float = 30) -> Optional[Tuple[str, List[str]]]:
    """负载均衡的翻译函数，带重试机制
    
    Args:
        text: 要翻译的文本
        source_lang: 源语言
        target_lang: 目标语言
        load_balancer: 负载均衡器
        max_retries: 最大重试次数
        timeout: 单个条目的超时时间（秒）
    
    Returns:
        Optional[Tuple[str, List[str]]]: 翻译结果和备选翻译，如果全部失败则返回None
    """
    if not load_balancer:
        return None
    
    start_time = time.time()
    attempts = 0
    
    while attempts < max_retries:
        # 检查是否超时
        if time.time() - start_time > timeout:
            print(f"翻译超时（{timeout}秒）")
            return None
            
        service = load_balancer.get_next_service()
        if not service:
            print("没有可用的翻译服务")
            time.sleep(1)  # 等待1秒后重试
            attempts += 1
            continue
        
        try:
            result = service.make_request(text, source_lang, target_lang)
            if result:
                load_balancer.mark_success(service)
                return result.text, result.alternatives
            else:
                load_balancer.mark_failure(service)
                print(f"翻译失败，服务：{service.name.value}，尝试下一个服务")
                attempts += 1
                
        except requests.exceptions.RequestException as e:
            load_balancer.mark_failure(service)
            print(f"请求出错，服务：{service.name.value}，错误：{str(e)}，尝试下一个服务")
            attempts += 1
            
        # 在重试之前短暂等待
        if attempts < max_retries:
            time.sleep(1)
    
    print(f"所有翻译服务尝试失败（{max_retries}次）")
    return None

def create_default_load_balancer(tokenMissuo=None, tokenLinuxdo=None) -> TranslationLoadBalancer:
    """创建默认的负载均衡器，根据提供的token决定是否添加付费服务"""
    balancer = TranslationLoadBalancer()
    
    # 定义所有可能的服务
    services = []
    
    # 只在提供token时添加付费服务
    if tokenMissuo:
        services.append(
            TranslationService(
                name=ServiceType.MISSUO,
                base_url="https://deeplx.missuo.ru/translate",
                token=tokenMissuo,
                weight=1
            )
        )
    
    if tokenLinuxdo:
        services.append(
            TranslationService(
                name=ServiceType.LINUXDO,
                base_url="https://api.deeplx.org/translate",
                token=tokenLinuxdo,
                weight=2
            )
        )
    
    # 添加免费服务
    services.extend([
        TranslationService(
            name=ServiceType.FINDMYIP,
            base_url="https://findmyip.net/api/translate.php",
            method="GET",
            weight=2
        ),
        TranslationService(
            name=ServiceType.EDU6,
            base_url="https://deeplx.edu6.eu.org/translate",
            token="666666",
            weight=4
        ),
        TranslationService(
            name=ServiceType.SMNET,
            base_url="https://deeplx.smnet.io/translate",
            weight=10
        )
    ])
    
    # 将所有服务添加到负载均衡器
    for service in services:
        balancer.add_service(service)
    
    return balancer

def main():
    # 创建负载均衡器
    balancer = create_default_load_balancer()
    
    # 测试文本
    test_texts = [
        ("Hello, how are you?", "en", "zh"),
        ("这是一个测试消息", "zh", "en"),
        ("안녕하세요", "ko", "zh"),
        ("Hello, how are you?", "en", "zh"),
    ]
    
    # 测试翻译
    for text, source, target in test_texts:
        print(f"\n原文: {text}")
        result = translate_text(text, source_lang=source, target_lang=target, 
                             load_balancer=balancer, max_retries=5, timeout=10)
        if result:
            main_text, alternatives = result
            print(f"译文: {main_text}")
            if alternatives:
                print("备选翻译:")
                for i, alt in enumerate(alternatives, 1):
                    print(f"  {i}. {alt}")
        time.sleep(1)  # 避免请求过于频繁

if __name__ == "__main__":
    main()