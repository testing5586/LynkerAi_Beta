#!/usr/bin/env python3
"""
简洁版 Master AI 文件上传 API
- 安全的文件类型验证
- 大小限制
- 自动导入到 Vault
"""

from flask import Flask, request, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_EXT = {"md", "txt", "pdf", "docx"}
MAX_SIZE_MB = 10

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route("/api/master-ai/upload", methods=["POST"])
def upload_file():
    """上传文件并导入 Lynker Master Vault"""
    if "file" not in request.files:
        return jsonify({"error": "❌ 未检测到文件"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "❌ 文件名为空"}), 400

    if not allowed_file(f.filename):
        return jsonify({"error": f"❌ 不支持的文件类型: {f.filename}"}), 400

    # 检查文件大小
    f.seek(0, os.SEEK_END)
    size_mb = f.tell() / (1024 * 1024)
    f.seek(0)
    if size_mb > MAX_SIZE_MB:
        return jsonify({"error": f"⚠️ 文件超过 {MAX_SIZE_MB}MB 限制"}), 400

    # 安全处理文件名
    safe_name = secure_filename(f.filename or "")
    filepath = os.path.join(UPLOAD_DIR, safe_name)
    f.save(filepath)

    # 调用导入器执行自动分类
    result = subprocess.getoutput(f"python master_ai_importer.py import {filepath}")
    
    return jsonify({
        "status": "✅ 文件上传并导入成功",
        "filename": safe_name,
        "import_result": result
    })

@app.route("/api/master-ai/context", methods=["GET"])
def get_context():
    """查看 Vault 中的文件列表"""
    context = {}
    vault_path = "lynker_master_vault"
    
    if not os.path.exists(vault_path):
        return jsonify({"error": "Vault 不存在"}), 404
    
    for root, dirs, files in os.walk(vault_path):
        rel_root = os.path.relpath(root, vault_path)
        if files:  # 只显示有文件的目录
            context[rel_root] = files
    
    return jsonify(context)

@app.route("/")
def index():
    return """
    <html>
    <head><title>Lynker Master Vault Upload API</title></head>
    <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
        <h2>✅ Lynker Master Vault Upload API 正在运行</h2>
        <p>📍 可用端点：</p>
        <ul>
            <li><code>POST /api/master-ai/upload</code> - 上传文件</li>
            <li><code>GET /api/master-ai/context</code> - 查看 Vault 状态</li>
        </ul>
        <p>📚 <a href="/api/master-ai/context">查看当前 Vault 内容</a></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Lynker Master Vault Upload API")
    print("=" * 60)
    print("📍 端点:")
    print("   POST /api/master-ai/upload   - 上传文件")
    print("   GET  /api/master-ai/context  - 查看 Vault")
    print("=" * 60)
    app.run(host="0.0.0.0", port=8008)
