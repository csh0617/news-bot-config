from flask import Flask, request, render_template, redirect
import json
import os

app = Flask(__name__)
USERS_FILE = "users.json"
CONFIG_FILE = "config.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = request.form.get("user", "").strip()
        chat_id = request.form.get("chat_id", "").strip()
        keyword = request.form.get("keyword", "").strip()
        users = load_users()
        for u in users:
            if u["user"] == user:
                if keyword and keyword not in u["keywords"]:
                    u["keywords"].append(keyword)
                u["chat_id"] = chat_id
                break
        else:
            if user and chat_id and keyword:
                users.append({
                    "user": user,
                    "chat_id": chat_id,
                    "keywords": [keyword]
                })
        save_users(users)
        return redirect("/")
    return render_template("index.html", users=load_users())

@app.route("/delete", methods=["POST"])
def delete_keyword():
    user = request.form.get("user", "").strip()
    keyword = request.form.get("keyword", "").strip()
    users = load_users()
    for u in users:
        if u["user"] == user and keyword in u["keywords"]:
            u["keywords"].remove(keyword)
    save_users(users)
    return redirect("/")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        token = request.form.get("telegram_token", "").strip()
        interval = int(request.form.get("interval", 1800))
        save_config({
            "telegram_token": token,
            "interval": interval
        })
        return redirect("/settings")
    return render_template("settings.html", config=load_config())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
