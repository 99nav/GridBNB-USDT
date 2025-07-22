"""
推送通知管理器
统一管理多种推送方式，支持优先级和备用方案
"""

import logging
from typing import List, Optional, Dict, Any
from notification_providers import (
    NotificationProvider,
    PushPlusProvider,
    BarkProvider,
    DingTalkProvider,
    WeChatWorkProvider,
    FeishuProvider,
    TelegramProvider
)
from config import settings


class NotificationManager:
    """推送通知管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("NotificationManager")
        self.providers: Dict[str, NotificationProvider] = {}
        self.enabled_providers: List[str] = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """初始化所有推送提供者"""
        # 注册所有可用的推送提供者
        self.providers = {
            'pushplus': PushPlusProvider(),
            'bark': BarkProvider(),
            'dingtalk': DingTalkProvider(),
            'wechat_work': WeChatWorkProvider(),
            'feishu': FeishuProvider(),
            'telegram': TelegramProvider(),
        }
        
        # 从配置中获取启用的推送方式
        enabled_providers_config = getattr(settings, 'NOTIFICATION_PROVIDERS', 'pushplus')
        if isinstance(enabled_providers_config, str):
            self.enabled_providers = [p.strip() for p in enabled_providers_config.split(',') if p.strip()]
        else:
            self.enabled_providers = enabled_providers_config or ['pushplus']
        
        # 验证配置的推送方式是否有效
        valid_providers = []
        for provider_name in self.enabled_providers:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.is_configured():
                    valid_providers.append(provider_name)
                    self.logger.info(f"推送提供者 {provider_name} 已配置并启用")
                else:
                    self.logger.warning(f"推送提供者 {provider_name} 未正确配置，已跳过")
            else:
                self.logger.error(f"未知的推送提供者: {provider_name}")
        
        self.enabled_providers = valid_providers
        
        if not self.enabled_providers:
            self.logger.warning("没有可用的推送提供者，推送功能将被禁用")
        else:
            self.logger.info(f"已启用的推送提供者: {', '.join(self.enabled_providers)}")
    
    def send_notification(
        self, 
        content: str, 
        title: str = "交易信号通知", 
        providers: Optional[List[str]] = None,
        **kwargs
    ) -> bool:
        """
        发送推送通知
        
        Args:
            content: 推送内容
            title: 推送标题
            providers: 指定使用的推送提供者列表，如果为None则使用所有启用的提供者
            **kwargs: 其他推送参数
            
        Returns:
            bool: 是否至少有一个推送成功
        """
        if not self.enabled_providers:
            self.logger.warning("没有可用的推送提供者，无法发送通知")
            return False
        
        # 确定要使用的推送提供者
        target_providers = providers if providers else self.enabled_providers
        
        # 过滤出有效且已配置的提供者
        valid_providers = [
            name for name in target_providers 
            if name in self.providers and name in self.enabled_providers
        ]
        
        if not valid_providers:
            self.logger.error("没有有效的推送提供者可用")
            return False
        
        success_count = 0
        total_count = len(valid_providers)
        
        # 按顺序尝试每个推送提供者
        for provider_name in valid_providers:
            provider = self.providers[provider_name]
            try:
                if provider.send(content, title, **kwargs):
                    success_count += 1
                    self.logger.info(f"通过 {provider_name} 推送成功")
                else:
                    self.logger.warning(f"通过 {provider_name} 推送失败")
            except Exception as e:
                self.logger.error(f"推送提供者 {provider_name} 发生异常: {str(e)}", exc_info=True)
        
        # 记录推送结果
        if success_count > 0:
            self.logger.info(f"推送完成: {success_count}/{total_count} 个提供者成功")
            return True
        else:
            self.logger.error(f"推送失败: 所有 {total_count} 个提供者都失败了")
            return False
    
    def send_notification_with_fallback(
        self, 
        content: str, 
        title: str = "交易信号通知",
        **kwargs
    ) -> bool:
        """
        发送推送通知（带备用方案）
        按优先级顺序尝试，只要有一个成功就停止
        
        Args:
            content: 推送内容
            title: 推送标题
            **kwargs: 其他推送参数
            
        Returns:
            bool: 是否推送成功
        """
        if not self.enabled_providers:
            self.logger.warning("没有可用的推送提供者，无法发送通知")
            return False
        
        # 按配置顺序尝试每个推送提供者，成功一个就停止
        for provider_name in self.enabled_providers:
            provider = self.providers[provider_name]
            try:
                if provider.send(content, title, **kwargs):
                    self.logger.info(f"通过 {provider_name} 推送成功")
                    return True
                else:
                    self.logger.warning(f"通过 {provider_name} 推送失败，尝试下一个提供者")
            except Exception as e:
                self.logger.error(f"推送提供者 {provider_name} 发生异常: {str(e)}，尝试下一个提供者", exc_info=True)
        
        self.logger.error("所有推送提供者都失败了")
        return False
    
    def get_available_providers(self) -> List[str]:
        """获取所有可用的推送提供者列表"""
        return list(self.providers.keys())
    
    def get_enabled_providers(self) -> List[str]:
        """获取已启用的推送提供者列表"""
        return self.enabled_providers.copy()
    
    def is_provider_configured(self, provider_name: str) -> bool:
        """检查指定的推送提供者是否已配置"""
        if provider_name not in self.providers:
            return False
        return self.providers[provider_name].is_configured()


# 创建全局推送管理器实例
notification_manager = NotificationManager()


def send_notification(
    content: str, 
    title: str = "交易信号通知", 
    providers: Optional[List[str]] = None,
    use_fallback: bool = True,
    **kwargs
) -> bool:
    """
    发送推送通知的便捷函数
    
    Args:
        content: 推送内容
        title: 推送标题
        providers: 指定使用的推送提供者列表
        use_fallback: 是否使用备用方案（只要一个成功就停止）
        **kwargs: 其他推送参数
        
    Returns:
        bool: 是否推送成功
    """
    if use_fallback and not providers:
        # 使用备用方案：按优先级顺序尝试，成功一个就停止
        return notification_manager.send_notification_with_fallback(content, title, **kwargs)
    else:
        # 使用指定的提供者或所有启用的提供者
        return notification_manager.send_notification(content, title, providers, **kwargs)


def get_notification_status() -> Dict[str, Any]:
    """
    获取推送系统状态信息
    
    Returns:
        Dict: 包含推送系统状态的字典
    """
    return {
        'available_providers': notification_manager.get_available_providers(),
        'enabled_providers': notification_manager.get_enabled_providers(),
        'provider_status': {
            name: notification_manager.is_provider_configured(name)
            for name in notification_manager.get_available_providers()
        }
    }
