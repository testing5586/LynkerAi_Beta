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
        <p>📤 <a href="/upload" style="color: #007bff; font-weight: bold;">手动上传文件测试</a></p>
    </body>
    </html>
    """

@app.route("/upload")
def upload_page():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lynker Master Vault 文件上传测试</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 28px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            .upload-area {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 40px;
                text-align: center;
                background: #f8f9ff;
                transition: all 0.3s;
                cursor: pointer;
            }
            .upload-area:hover {
                background: #eef0ff;
                border-color: #764ba2;
            }
            .upload-icon {
                font-size: 64px;
                margin-bottom: 20px;
            }
            input[type="file"] {
                display: none;
            }
            .file-label {
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                border-radius: 25px;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s;
            }
            .file-label:hover {
                background: #764ba2;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102,126,234,0.3);
            }
            .submit-btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin-top: 20px;
                transition: all 0.3s;
            }
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102,126,234,0.4);
            }
            .submit-btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .file-info {
                margin-top: 20px;
                padding: 15px;
                background: #e8f5e9;
                border-radius: 10px;
                color: #2e7d32;
                display: none;
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                border-radius: 10px;
                display: none;
            }
            .result.success {
                background: #e8f5e9;
                color: #2e7d32;
                border-left: 5px solid #4caf50;
            }
            .result.error {
                background: #ffebee;
                color: #c62828;
                border-left: 5px solid #f44336;
            }
            .allowed-types {
                margin-top: 20px;
                padding: 15px;
                background: #fff3e0;
                border-radius: 10px;
                font-size: 13px;
                color: #e65100;
            }
            .back-link {
                display: inline-block;
                margin-top: 20px;
                color: #667eea;
                text-decoration: none;
                font-weight: bold;
            }
            .back-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📤 Lynker Master Vault</h1>
            <div class="subtitle">文件上传测试工具</div>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon">📁</div>
                    <label for="fileInput" class="file-label">选择文件</label>
                    <input type="file" id="fileInput" name="file" accept=".md,.txt,.pdf,.docx">
                    <p style="margin-top: 15px; color: #666;">点击或拖拽文件到此区域</p>
                </div>
                
                <div class="file-info" id="fileInfo"></div>
                
                <button type="submit" class="submit-btn" id="submitBtn" disabled>
                    上传到 Vault
                </button>
            </form>
            
            <div class="allowed-types">
                ✅ 支持的文件类型: .md, .txt, .pdf, .docx<br>
                📊 最大文件大小: 10MB
            </div>
            
            <div class="result" id="result"></div>
            
            <a href="/" class="back-link">← 返回首页</a>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const submitBtn = document.getElementById('submitBtn');
            const uploadForm = document.getElementById('uploadForm');
            const resultDiv = document.getElementById('result');

            fileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                    fileInfo.innerHTML = `📄 已选择: <strong>${file.name}</strong> (${sizeMB} MB)`;
                    fileInfo.style.display = 'block';
                    submitBtn.disabled = false;
                }
            });

            uploadForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData();
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('请先选择文件！');
                    return;
                }
                
                formData.append('file', file);
                submitBtn.disabled = true;
                submitBtn.textContent = '上传中...';
                resultDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/master-ai/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <strong>✅ ${data.status}</strong><br>
                            <div style="margin-top: 10px;">
                                📄 文件名: ${data.filename}<br>
                                📝 导入结果:<br>
                                <pre style="background: white; padding: 10px; border-radius: 5px; margin-top: 10px; overflow-x: auto;">${data.import_result}</pre>
                            </div>
                        `;
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<strong>❌ 上传失败</strong><br>${data.error || '未知错误'}`;
                    }
                    
                    resultDiv.style.display = 'block';
                    
                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>❌ 网络错误</strong><br>${error.message}`;
                    resultDiv.style.display = 'block';
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '上传到 Vault';
                    fileInput.value = '';
                    fileInfo.style.display = 'none';
                }
            });
        </script>
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
