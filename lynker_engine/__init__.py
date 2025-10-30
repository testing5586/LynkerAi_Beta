# Lynker Engine Package
"""
LynkerAI 核心引擎包
包含验证管理器和其他核心功能模块
"""

from .core.validation_manager import (
    generate_statement_id,
    is_fortune_statement,
    append_truth_buttons,
    extract_statements_from_text,
    format_ai_response,
    parse_validation_click,
    create_validation_log,
    get_predefined_statement
)

__all__ = [
    'generate_statement_id',
    'is_fortune_statement',
    'append_truth_buttons',
    'extract_statements_from_text',
    'format_ai_response',
    'parse_validation_click',
    'create_validation_log',
    'get_predefined_statement'
]