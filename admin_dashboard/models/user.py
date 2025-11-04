"""
用户模型和数据库操作
整合 LynkerAi Registration 用户系统到当前项目
"""
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(
        os.environ['DATABASE_URL'],
        cursor_factory=RealDictCursor
    )

class User(UserMixin):
    """
    Flask-Login 用户类
    兼容现有 users 表结构
    """
    def __init__(self, user_data):
        self.id = str(user_data.get('id'))  # UUID
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.profile_image_url = user_data.get('profile_image_url')
        self.is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at')
        
        # 用户类型缓存
        self._user_type = None
    
    def get_id(self):
        """Flask-Login 需要的方法"""
        return self.id
    
    @property
    def user_type(self):
        """获取用户类型（guru 或 normal_user）"""
        if self._user_type is None:
            self._user_type = get_user_type(self.id)
        return self._user_type
    
    @property
    def profile(self):
        """获取用户档案（根据类型返回不同的档案）"""
        if self.user_type == 'guru':
            return get_guru_profile(self.id)
        elif self.user_type == 'normal_user':
            return get_normal_user_profile(self.id)
        return None


# ==================== 用户 CRUD 操作 ====================

def create_user(email, password, first_name=None, last_name=None):
    """
    创建新用户
    Args:
        email: 邮箱
        password: 明文密码
        first_name: 名字（可选）
        last_name: 姓氏（可选）
    Returns:
        User 对象或 None
    """
    try:
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 创建用户记录
        cur.execute("""
            INSERT INTO users (id, email, password_hash, first_name, last_name, name, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (user_id, email, password_hash, first_name, last_name, email, True))
        
        user_data = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return User(user_data) if user_data else None
    except psycopg2.IntegrityError as e:
        print(f"[User] 创建用户失败（邮箱已存在）: {e}")
        return None
    except Exception as e:
        print(f"[User] 创建用户失败: {e}")
        return None


def get_user_by_id(user_id):
    """通过 ID 获取用户"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return User(user_data) if user_data else None
    except Exception as e:
        print(f"[User] 获取用户失败: {e}")
        return None


def get_user_by_email(email):
    """通过邮箱获取用户"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return User(user_data) if user_data else None
    except Exception as e:
        print(f"[User] 获取用户失败: {e}")
        return None


def verify_password(user, password):
    """
    验证密码
    Args:
        user: User 对象
        password: 明文密码
    Returns:
        bool
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT password_hash FROM users WHERE id = %s", (user.id,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result and result['password_hash']:
            return bcrypt.check_password_hash(result['password_hash'], password)
        return False
    except Exception as e:
        print(f"[User] 验证密码失败: {e}")
        return False


def get_user_type(user_id):
    """
    判断用户类型
    Returns:
        'guru' | 'normal_user' | 'new_user'
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 检查是否是命理师
        cur.execute("SELECT id FROM guru_profiles WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return 'guru'
        
        # 检查是否是普通用户
        cur.execute("SELECT id FROM normal_user_profiles WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return 'normal_user'
        
        cur.close()
        conn.close()
        return 'new_user'
    except Exception as e:
        print(f"[User] 获取用户类型失败: {e}")
        return 'new_user'


# ==================== 普通用户档案 CRUD ====================

def create_normal_user_profile(user_id, pseudonym, **kwargs):
    """
    创建普通用户档案
    Args:
        user_id: 用户 UUID
        pseudonym: 灵性假名（必填）
        **kwargs: 可选字段（gender, birth_date, preferred_provider 等）
    Returns:
        dict 档案数据或 None
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        profile_id = str(uuid.uuid4())
        
        cur.execute("""
            INSERT INTO normal_user_profiles 
            (id, user_id, pseudonym, gender, birth_date, birth_time, birth_location, 
             preferred_provider, preferred_language, avatar_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            profile_id,
            user_id,
            pseudonym,
            kwargs.get('gender'),
            kwargs.get('birth_date'),
            kwargs.get('birth_time'),
            kwargs.get('birth_location'),
            kwargs.get('preferred_provider', 'LocalMock'),
            kwargs.get('preferred_language', 'zh'),
            kwargs.get('avatar_url')
        ))
        
        profile = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[NormalProfile] 创建成功: {pseudonym} (user_id: {user_id})")
        return dict(profile) if profile else None
    except psycopg2.IntegrityError:
        print(f"[NormalProfile] 用户档案已存在")
        return None
    except Exception as e:
        print(f"[NormalProfile] 创建失败: {e}")
        return None


def get_normal_user_profile(user_id):
    """获取普通用户档案"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM normal_user_profiles WHERE user_id = %s", (user_id,))
        profile = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(profile) if profile else None
    except Exception as e:
        print(f"[NormalProfile] 获取失败: {e}")
        return None


# ==================== 命理师档案 CRUD ====================

def create_guru_profile(user_id, pseudonym, bio, specializations, **kwargs):
    """
    创建命理师档案
    Args:
        user_id: 用户 UUID
        pseudonym: 灵性假名
        bio: 个人简介
        specializations: 专长列表 ['bazi', 'ziwei', 'iching', 'tarot']
        **kwargs: 可选字段
    Returns:
        dict 档案数据或 None
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        profile_id = str(uuid.uuid4())
        
        cur.execute("""
            INSERT INTO guru_profiles 
            (id, user_id, pseudonym, bio, specializations, region, nationality,
             ai_provider, ai_tone, avatar_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            profile_id,
            user_id,
            pseudonym,
            bio,
            specializations,  # PostgreSQL 数组
            kwargs.get('region'),
            kwargs.get('nationality'),
            kwargs.get('ai_provider', 'LocalMock'),
            kwargs.get('ai_tone', 'professional'),
            kwargs.get('avatar_url')
        ))
        
        profile = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[GuruProfile] 创建成功: {pseudonym} (user_id: {user_id})")
        return dict(profile) if profile else None
    except psycopg2.IntegrityError:
        print(f"[GuruProfile] 命理师档案已存在")
        return None
    except Exception as e:
        print(f"[GuruProfile] 创建失败: {e}")
        return None


def get_guru_profile(user_id):
    """获取命理师档案"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM guru_profiles WHERE user_id = %s", (user_id,))
        profile = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return dict(profile) if profile else None
    except Exception as e:
        print(f"[GuruProfile] 获取失败: {e}")
        return None


# ==================== 工具函数 ====================

def validate_pseudonym(pseudonym):
    """
    验证灵性假名（不能是真名格式）
    Returns:
        (bool, str) (是否有效, 错误消息)
    """
    import re
    
    if len(pseudonym) < 2:
        return False, "灵性假名至少需要 2 个字符"
    
    # 检查是否为真名模式
    real_name_patterns = [
        r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # John Smith
        r'^(Mr|Mrs|Ms|Dr)\.',           # 头衔
    ]
    
    for pattern in real_name_patterns:
        if re.match(pattern, pseudonym, re.IGNORECASE):
            return False, "请使用灵性假名，而非真实姓名"
    
    return True, ""
