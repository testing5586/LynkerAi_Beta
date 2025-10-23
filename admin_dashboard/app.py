from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit
from auth import verify_login
from data_fetcher import get_dashboard_data
from chat_hub import process_message

app = Flask(__name__)
app.secret_key = "lynker_dashboard_session"
socketio = SocketIO(app, cors_allowed_origins="*")

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
    return render_template("chatroom.html")

@socketio.on("send_message")
def handle_message(data):
    user_msg = data["message"]
    responses = process_message(user_msg)
    emit("receive_message", responses, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
