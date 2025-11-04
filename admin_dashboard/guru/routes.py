"""
命理师路由
"""
from flask import Blueprint, render_template, redirect
from flask_login import login_required, current_user

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')


@guru_bp.route('/dashboard')
@login_required
def dashboard():
    """命理师仪表盘"""
    # 检查是否已创建档案
    if current_user.user_type == 'new_user':
        return redirect('/guru-register')
    
    # 获取命理师档案
    profile = current_user.profile
    
    return render_template('guru/dashboard.html', profile=profile)
