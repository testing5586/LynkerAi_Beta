"""
LynkerAI Core Module
包含核心功能模块
"""

from .validation_manager import (
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