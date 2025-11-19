"""
AI 代理层 Django 应用配置
"""

from django.apps import AppConfig


class AIProxyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_proxy"
    verbose_name = "AI 代理层"

    def ready(self):
        """应用启动时执行"""
        # 可以在这里注册信号处理器等
        pass
