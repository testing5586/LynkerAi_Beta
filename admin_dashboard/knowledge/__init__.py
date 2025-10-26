"""
Knowledge Retrieval Router for LynkerAI
知识检索总线 - 为三位 AI 提供命理知识增强
"""

from .retrieval_router import find_relevant_knowledge
from .access_control import allow_access

__all__ = ['find_relevant_knowledge', 'allow_access']
