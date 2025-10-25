from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
from auth import verify_login
from data_fetcher import get_dashboard_data
from chat_hub_v2 import process_message, get_agent_info

import os

app = Flask(__name__)
app.secret_key = os.getenv("MASTER_VAULT_KEY")
if not app.secret_key:
    raise ValueError("MASTER_VAULT_KEY environment variable must be set for secure session management")
socketio = SocketIO(app, cors_allowed_origins="*")

# 注册用户事件追踪 Blueprint
from user_events.event_api import event_bp
app.register_blueprint(event_bp)
print("✅ 用户事件追踪 API 已注册: /api/events/track, /api/insights/<user_id>")

@app.route("/")
def index():
    return redirect("/admin")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if verify_login(password):
            session["auth"] = True
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("auth"):
        return redirect("/admin")
    data = get_dashboard_data()
    return render_template("dashboard.html", data=data)

@app.route("/chatroom")
def chatroom():
    if not session.get("auth"):
        return redirect("/admin")
    agent_info = get_agent_info()
    return render_template("chatroom.html", agents=agent_info)

@socketio.on("send_message")
def handle_message(data):
    user_msg = data["message"]
    responses = process_message(user_msg)
    emit("receive_message", responses, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
