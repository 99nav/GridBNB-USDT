"""
推送通知提供者模块
支持多种推送方式的统一接口和具体实现
"""

import logging
import requests
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from config import settings


class NotificationProvider(ABC):
    """推送通知提供者抽象基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"NotificationProvider.{name}")
    
    @abstractmethod
    def is_configured(self) -> bool:
        """检查是否已正确配置"""
        pass
    
    @abstractmethod
    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """
        发送推送通知
        
        Args:
            content: 推送内容
            title: 推送标题
            **kwargs: 其他推送参数
            
        Returns:
            bool: 发送是否成功
        """
        pass


class PushPlusProvider(NotificationProvider):
    """PushPlus推送提供者"""
    
    def __init__(self):
        super().__init__("PushPlus")
        self.token = settings.PUSHPLUS_TOKEN
        self.url = os.getenv('PUSHPLUS_URL', 'https://www.pushplus.plus/send')
        self.timeout = settings.PUSHPLUS_TIMEOUT
    
    def is_configured(self) -> bool:
        """检查PushPlus是否已配置"""
        return bool(self.token)
    
    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """发送PushPlus推送"""
        if not self.is_configured():
            self.logger.error("PushPlus未配置TOKEN，无法发送通知")
            return False
        
        data = {
            "token": self.token,
            "title": title,
            "content": content,
            "template": kwargs.get("template", "txt")
        }
        
        try:
            self.logger.info(f"正在通过PushPlus发送推送通知: {title}")
            response = requests.post(self.url, data=data, timeout=self.timeout)
            response_json = response.json()
            
            if response.status_code == 200 and response_json.get('code') == 200:
                self.logger.info(f"PushPlus推送成功: {content}")
                return True
            else:
                self.logger.error(f"PushPlus推送失败: 状态码={response.status_code}, 响应={response_json}")
                return False
                
        except Exception as e:
            self.logger.error(f"PushPlus推送异常: {str(e)}", exc_info=True)
            return False


class BarkProvider(NotificationProvider):
    """Bark推送提供者"""
    
    def __init__(self):
        super().__init__("Bark")
        self.device_token = getattr(settings, 'BARK_DEVICE_TOKEN', None)
        self.server_url = getattr(settings, 'BARK_SERVER_URL', 'https://api.day.app')
        self.timeout = getattr(settings, 'BARK_TIMEOUT', 5)
    
    def is_configured(self) -> bool:
        """检查Bark是否已配置"""
        return bool(self.device_token)
    
    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """发送Bark推送"""
        if not self.is_configured():
            self.logger.error("Bark未配置DEVICE_TOKEN，无法发送通知")
            return False

        try:
            self.logger.info(f"正在通过Bark发送推送通知: {title}")

            # 方法1: 尝试POST方式（推荐，支持长内容）
            success = self._send_post(title, content, **kwargs)
            if success:
                return True

            # 方法2: 如果POST失败，尝试GET方式（兼容性更好）
            self.logger.info("POST方式失败，尝试GET方式...")
            success = self._send_get(title, content, **kwargs)
            return success

        except Exception as e:
            self.logger.error(f"Bark推送异常: {str(e)}", exc_info=True)
            return False

    def _send_post(self, title: str, content: str, **kwargs) -> bool:
        """使用POST方式发送Bark推送"""
        try:
            url = f"{self.server_url}/{self.device_token}"

            # 构建POST数据
            data = {
                "title": title,
                "body": content
            }

            # 添加可选参数
            if 'url' in kwargs:
                data['url'] = kwargs['url']
            if 'group' in kwargs:
                data['group'] = kwargs['group']
            if 'icon' in kwargs:
                data['icon'] = kwargs['icon']
            if 'sound' in kwargs:
                data['sound'] = kwargs['sound']
            if 'level' in kwargs:
                data['level'] = kwargs['level']
            if 'copy' in kwargs:
                data['copy'] = kwargs['copy']

            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)

            return self._handle_response(response, "POST")

        except Exception as e:
            self.logger.warning(f"POST方式发送失败: {e}")
            return False

    def _send_get(self, title: str, content: str, **kwargs) -> bool:
        """使用GET方式发送Bark推送（兼容性更好）"""
        try:
            # 限制内容长度，避免URL过长
            max_content_length = 100
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."

            # 构建GET URL（简化版本，避免编码问题）
            import urllib.parse
            encoded_title = urllib.parse.quote(title)
            encoded_content = urllib.parse.quote(content)

            url = f"{self.server_url}/{self.device_token}/{encoded_title}/{encoded_content}"

            # 添加可选参数
            params = {}
            if 'url' in kwargs:
                params['url'] = kwargs['url']
            if 'group' in kwargs:
                params['group'] = kwargs['group']
            if 'sound' in kwargs:
                params['sound'] = kwargs['sound']

            response = requests.get(url, params=params, timeout=self.timeout)

            return self._handle_response(response, "GET")

        except Exception as e:
            self.logger.warning(f"GET方式发送失败: {e}")
            return False

    def _handle_response(self, response, method: str) -> bool:
        """处理Bark API响应"""
        if response.status_code == 200:
            try:
                response_json = response.json()
                if response_json.get('code') == 200:
                    self.logger.info(f"Bark推送成功 ({method})")
                    return True
                else:
                    self.logger.error(f"Bark推送失败 ({method}): {response_json.get('message', '未知错误')}")
                    return False
            except ValueError:
                # 某些情况下响应可能不是JSON，但状态码200表示成功
                self.logger.info(f"Bark推送成功 ({method}) - 响应格式异常但状态码正常")
                return True
        else:
            try:
                response_json = response.json()
                error_msg = response_json.get('message', '未知错误')
                self.logger.error(f"Bark推送失败 ({method}): 状态码={response.status_code}, 错误={error_msg}")
            except ValueError:
                self.logger.error(f"Bark推送失败 ({method}): 状态码={response.status_code}, 响应={response.text[:100]}")
            return False


class DingTalkProvider(NotificationProvider):
    """钉钉机器人推送提供者"""
    
    def __init__(self):
        super().__init__("DingTalk")
        self.webhook_url = getattr(settings, 'DINGTALK_WEBHOOK_URL', None)
        self.secret = getattr(settings, 'DINGTALK_SECRET', None)
        self.timeout = getattr(settings, 'DINGTALK_TIMEOUT', 5)
    
    def is_configured(self) -> bool:
        """检查钉钉是否已配置"""
        return bool(self.webhook_url)
    
    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """发送钉钉推送"""
        if not self.is_configured():
            self.logger.error("钉钉未配置WEBHOOK_URL，无法发送通知")
            return False
        
        # 构建钉钉消息格式
        data = {
            "msgtype": "text",
            "text": {
                "content": f"{title}\n\n{content}"
            }
        }
        
        # 如果配置了关键词，添加@all
        if kwargs.get('at_all', False):
            data["at"] = {"isAtAll": True}
        
        try:
            self.logger.info(f"正在通过钉钉发送推送通知: {title}")
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url, 
                json=data, 
                headers=headers, 
                timeout=self.timeout
            )
            response_json = response.json()
            
            if response.status_code == 200 and response_json.get('errcode') == 0:
                self.logger.info(f"钉钉推送成功: {content}")
                return True
            else:
                self.logger.error(f"钉钉推送失败: 状态码={response.status_code}, 响应={response_json}")
                return False
                
        except Exception as e:
            self.logger.error(f"钉钉推送异常: {str(e)}", exc_info=True)
            return False


class WeChatWorkProvider(NotificationProvider):
    """企业微信机器人推送提供者"""

    def __init__(self):
        super().__init__("WeChatWork")
        self.webhook_url = getattr(settings, 'WECHAT_WORK_WEBHOOK_URL', None)
        self.timeout = getattr(settings, 'WECHAT_WORK_TIMEOUT', 5)

    def is_configured(self) -> bool:
        """检查企业微信是否已配置"""
        return bool(self.webhook_url)

    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """发送企业微信推送"""
        if not self.is_configured():
            self.logger.error("企业微信未配置WEBHOOK_URL，无法发送通知")
            return False

        # 构建企业微信消息格式
        data = {
            "msgtype": "text",
            "text": {
                "content": f"{title}\n\n{content}"
            }
        }

        try:
            self.logger.info(f"正在通过企业微信发送推送通知: {title}")

            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            response_json = response.json()

            if response.status_code == 200 and response_json.get('errcode') == 0:
                self.logger.info(f"企业微信推送成功: {content}")
                return True
            else:
                self.logger.error(f"企业微信推送失败: 状态码={response.status_code}, 响应={response_json}")
                return False

        except Exception as e:
            self.logger.error(f"企业微信推送异常: {str(e)}", exc_info=True)
            return False


class FeishuProvider(NotificationProvider):
    """飞书机器人推送提供者"""

    def __init__(self):
        super().__init__("Feishu")
        self.webhook_url = getattr(settings, 'FEISHU_WEBHOOK_URL', None)
        self.secret = getattr(settings, 'FEISHU_SECRET', None)
        self.timeout = getattr(settings, 'FEISHU_TIMEOUT', 5)

    def is_configured(self) -> bool:
        """检查飞书是否已配置"""
        return bool(self.webhook_url)

    def _generate_sign(self, timestamp: str) -> Optional[str]:
        """生成飞书签名"""
        if not self.secret:
            return None

        import hmac
        import hashlib
        import base64

        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """发送飞书推送"""
        if not self.is_configured():
            self.logger.error("飞书未配置WEBHOOK_URL，无法发送通知")
            return False

        # 构建飞书消息格式
        data = {
            "msg_type": "text",
            "content": {
                "text": f"{title}\n\n{content}"
            }
        }

        # 如果配置了密钥，添加签名验证
        if self.secret:
            import time
            timestamp = str(int(time.time()))
            sign = self._generate_sign(timestamp)
            if sign:
                data["timestamp"] = timestamp
                data["sign"] = sign

        try:
            self.logger.info(f"正在通过飞书发送推送通知: {title}")

            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            response_json = response.json()

            if response.status_code == 200 and response_json.get('code') == 0:
                self.logger.info(f"飞书推送成功: {content}")
                return True
            else:
                self.logger.error(f"飞书推送失败: 状态码={response.status_code}, 响应={response_json}")
                return False

        except Exception as e:
            self.logger.error(f"飞书推送异常: {str(e)}", exc_info=True)
            return False


class TelegramProvider(NotificationProvider):
    """Telegram机器人推送提供者"""

    def __init__(self):
        super().__init__("Telegram")
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        self.timeout = getattr(settings, 'TELEGRAM_TIMEOUT', 5)

    def is_configured(self) -> bool:
        """检查Telegram是否已配置"""
        return bool(self.bot_token and self.chat_id)

    def send(self, content: str, title: str = "交易信号通知", **kwargs) -> bool:
        """发送Telegram推送"""
        if not self.is_configured():
            self.logger.error("Telegram未配置BOT_TOKEN或CHAT_ID，无法发送通知")
            return False

        # 构建Telegram API URL
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        # 构建消息内容
        message_text = f"*{title}*\n\n{content}"

        data = {
            "chat_id": self.chat_id,
            "text": message_text,
            "parse_mode": "Markdown",  # 支持Markdown格式
            "disable_web_page_preview": kwargs.get("disable_preview", True)
        }

        try:
            self.logger.info(f"正在通过Telegram发送推送通知: {title}")

            response = requests.post(url, json=data, timeout=self.timeout)
            response_json = response.json()

            if response.status_code == 200 and response_json.get('ok'):
                self.logger.info(f"Telegram推送成功: {content}")
                return True
            else:
                self.logger.error(f"Telegram推送失败: 状态码={response.status_code}, 响应={response_json}")
                return False

        except Exception as e:
            self.logger.error(f"Telegram推送异常: {str(e)}", exc_info=True)
            return False
