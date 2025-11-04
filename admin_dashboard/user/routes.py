"""
普通用户路由
"""
from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/home')
@login_required
def home():
    """普通用户主页"""
    # 检查是否已创建档案
    if current_user.user_type == 'new_user':
        return redirect('/user-register')
    
    # 获取用户档案
    profile = current_user.profile
    
    return render_template('user/home.html', profile=profile)
