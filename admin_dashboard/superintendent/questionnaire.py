"""
问卷管理中心 Blueprint
仅 admin & group_leader 可访问
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect
import os
import shutil
from datetime import datetime

bp_questionnaire = Blueprint("bp_questionnaire", __name__, url_prefix="/superintendent/questionnaire")

# 文件路径配置
CURRENT_VERSION_PATH = "data/true_birth_wizard_v1.txt"
HISTORY_DIR = "data/questionnaires/history"

def ensure_directories():
    """确保必要的目录存在"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    if not os.path.exists(CURRENT_VERSION_PATH):
        # 如果当前版本文件不存在，创建默认内容
        os.makedirs(os.path.dirname(CURRENT_VERSION_PATH), exist_ok=True)
        with open(CURRENT_VERSION_PATH, 'w', encoding='utf-8') as f:
            f.write("真命盘验证问卷 - 请通过管理后台上传问卷内容\n")

def check_auth():
    """检查用户是否已登录"""
    if not session.get("auth"):
        return False
    return True

@bp_questionnaire.route("/", methods=["GET"])
def page():
    """问卷管理中心首页"""
    if not check_auth():
        return redirect("/admin")
    
    ensure_directories()
    
    # 读取当前生效问卷
    try:
        with open(CURRENT_VERSION_PATH, 'r', encoding='utf-8') as f:
            current_content = f.read()
    except Exception as e:
        current_content = f"读取失败: {str(e)}"
    
    # 获取历史版本列表
    history_files = []
    try:
        if os.path.exists(HISTORY_DIR):
            files = sorted(os.listdir(HISTORY_DIR), reverse=True)
            for filename in files:
                if filename.endswith('.txt') or filename.endswith('.md'):
                    filepath = os.path.join(HISTORY_DIR, filename)
                    stat = os.stat(filepath)
                    history_files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
    except Exception as e:
        print(f"读取历史版本失败: {e}")
    
    return render_template(
        "superintendent/questionnaire.html",
        current_content=current_content,
        history_files=history_files
    )

@bp_questionnaire.route("/upload", methods=["POST"])
def upload():
    """上传新问卷文件"""
    if not check_auth():
        return jsonify({"ok": False, "message": "未授权"}), 401
    
    ensure_directories()
    
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({"ok": False, "message": "未找到上传文件"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"ok": False, "message": "文件名为空"}), 400
        
        # 检查文件格式
        if not file.filename or not (file.filename.endswith('.txt') or file.filename.endswith('.md')):
            return jsonify({"ok": False, "message": "仅支持 .txt 和 .md 格式"}), 400
        
        # 读取文件内容
        content = file.read().decode('utf-8')
        
        # 保存到历史目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        history_filename = f"{timestamp}.txt"
        history_path = os.path.join(HISTORY_DIR, history_filename)
        
        with open(history_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 备份当前版本到历史（如果存在）
        if os.path.exists(CURRENT_VERSION_PATH):
            backup_filename = f"backup_{timestamp}.txt"
            backup_path = os.path.join(HISTORY_DIR, backup_filename)
            shutil.copy2(CURRENT_VERSION_PATH, backup_path)
        
        # 更新当前生效版本
        with open(CURRENT_VERSION_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "ok": True,
            "message": f"问卷已更新！新版本已保存为 {history_filename}",
            "content": content
        })
    
    except Exception as e:
        return jsonify({"ok": False, "message": f"上传失败: {str(e)}"}), 500

@bp_questionnaire.route("/switch", methods=["POST"])
def switch_version():
    """切换到历史版本"""
    if not check_auth():
        return jsonify({"ok": False, "message": "未授权"}), 401
    
    try:
        data = request.json or {}
        filename = data.get('filename')
        
        if not filename:
            return jsonify({"ok": False, "message": "未指定文件名"}), 400
        
        history_path = os.path.join(HISTORY_DIR, filename)
        
        if not os.path.exists(history_path):
            return jsonify({"ok": False, "message": "历史版本文件不存在"}), 404
        
        # 备份当前版本
        if os.path.exists(CURRENT_VERSION_PATH):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"before_switch_{timestamp}.txt"
            backup_path = os.path.join(HISTORY_DIR, backup_filename)
            shutil.copy2(CURRENT_VERSION_PATH, backup_path)
        
        # 读取历史版本内容
        with open(history_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新当前版本
        with open(CURRENT_VERSION_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            "ok": True,
            "message": f"已切换到版本: {filename}",
            "content": content
        })
    
    except Exception as e:
        return jsonify({"ok": False, "message": f"切换失败: {str(e)}"}), 500

@bp_questionnaire.route("/preview/<filename>", methods=["GET"])
def preview(filename):
    """预览历史版本内容"""
    if not check_auth():
        return jsonify({"ok": False, "message": "未授权"}), 401
    
    try:
        history_path = os.path.join(HISTORY_DIR, filename)
        
        if not os.path.exists(history_path):
            return jsonify({"ok": False, "message": "文件不存在"}), 404
        
        with open(history_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            "ok": True,
            "content": content
        })
    
    except Exception as e:
        return jsonify({"ok": False, "message": f"预览失败: {str(e)}"}), 500
