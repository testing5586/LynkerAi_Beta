"""
知识库访问控制
控制谁可以查询知识库，防止外部绕过验证
"""
from typing import Optional, Set
from enum import Enum


class AccessLevel(Enum):
    """访问级别"""
    GUEST = 0           # 游客：无权限
    USER = 1            # 普通用户：只读 rules
    PRO = 2             # 付费用户：只读 rules + patterns
    ADMIN = 3           # 管理员：读写 rules + patterns
    SUPERINTENDENT = 4  # 超级管理员：完全访问 + case_study


class KnowledgeAccessControl:
    """
    知识库访问控制器
    """
    
    def __init__(self):
        # 定义各级别可访问的知识库类别
        self.access_map = {
            AccessLevel.GUEST: set(),
            AccessLevel.USER: {"rules"},
            AccessLevel.PRO: {"rules", "patterns"},
            AccessLevel.ADMIN: {"rules", "patterns"},
            AccessLevel.SUPERINTENDENT: {"rules", "patterns", "case_study"}
        }
        
        # 定义各级别可修改的知识库类别
        self.write_access_map = {
            AccessLevel.GUEST: set(),
            AccessLevel.USER: set(),
            AccessLevel.PRO: set(),
            AccessLevel.ADMIN: {"rules"},
            AccessLevel.SUPERINTENDENT: {"rules", "patterns", "case_study"}
        }
    
    def can_read(self, user_level: AccessLevel, category: str) -> bool:
        """
        检查用户是否有读权限
        
        Args:
            user_level: 用户级别
            category: 知识库类别 (rules/patterns/case_study)
            
        Returns:
            True if allowed, False otherwise
        """
        allowed_categories = self.access_map.get(user_level, set())
        return category in allowed_categories
    
    def can_write(self, user_level: AccessLevel, category: str) -> bool:
        """
        检查用户是否有写权限
        
        Args:
            user_level: 用户级别
            category: 知识库类别
            
        Returns:
            True if allowed, False otherwise
        """
        allowed_categories = self.write_access_map.get(user_level, set())
        return category in allowed_categories
    
    def filter_categories(self, user_level: AccessLevel, requested_categories: Optional[Set[str]] = None) -> Set[str]:
        """
        根据用户权限过滤类别
        
        Args:
            user_level: 用户级别
            requested_categories: 请求的类别集合，None 表示全部
            
        Returns:
            用户有权限访问的类别集合
        """
        allowed = self.access_map.get(user_level, set())
        
        if requested_categories is None:
            return allowed
        
        # 返回请求类别与允许类别的交集
        return allowed.intersection(requested_categories)
    
    def get_access_summary(self, user_level: AccessLevel) -> str:
        """
        获取用户访问权限摘要
        
        Args:
            user_level: 用户级别
            
        Returns:
            权限摘要字符串
        """
        read_access = self.access_map.get(user_level, set())
        write_access = self.write_access_map.get(user_level, set())
        
        return f"""
权限级别: {user_level.name}
可读取: {', '.join(read_access) if read_access else '无'}
可修改: {', '.join(write_access) if write_access else '无'}
        """.strip()


# 全局单例
_access_control = None

def get_access_control() -> KnowledgeAccessControl:
    """获取全局访问控制器实例"""
    global _access_control
    if _access_control is None:
        _access_control = KnowledgeAccessControl()
    return _access_control


def check_knowledge_access(user_level: str, category: str, operation: str = "read") -> bool:
    """
    便捷函数：检查知识库访问权限
    
    Args:
        user_level: 用户级别字符串 ("guest", "user", "pro", "admin", "superintendent")
        category: 知识库类别
        operation: 操作类型 ("read" or "write")
        
    Returns:
        True if allowed, False otherwise
    """
    try:
        level_enum = AccessLevel[user_level.upper()]
    except KeyError:
        print(f"⚠️ 无效的用户级别: {user_level}")
        return False
    
    controller = get_access_control()
    
    if operation == "read":
        return controller.can_read(level_enum, category)
    elif operation == "write":
        return controller.can_write(level_enum, category)
    else:
        print(f"⚠️ 无效的操作类型: {operation}")
        return False
