"""
真命盘验证中心 - 用户个人验证模块
提供 Wizard 问答 + 手写补充 + 命盘导入的三合一验证流程
"""
from verify.routes import bp as verify_wizard_bp

__all__ = ["verify_wizard_bp"]
