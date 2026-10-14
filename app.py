"""
Guestbook - phiên bản VIBE CODE
Flask + SQLite + đồng bộ data.json + thống kê Matplotlib

Chạy:  python app.py   ->  http://127.0.0.1:5000
"""
import json
import sqlite3
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # backend không cần GUI, bắt buộc khi chạy trong server
import matplotlib.pyplot as plt
from flask import (Flask, flash, g, redirect, render_template, request,
                   url_for)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "guestbook.db"
JSON_PATH = BASE_DIR / "data.json"
CHART_PATH = BASE_DIR / "static" / "stats.png"

MAX_NAME = 50
MAX_MESSAGE = 500

app = Flask(__name__)
app.secret_key = "doi-key-nay-khi-deploy"  # cần cho flash()


# ---------------------------------------------------------------- Database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Tạo bảng; nếu DB trống mà có data.json thì nạp dữ liệu từ file."""
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS entries (
               id         INTEGER PRIMARY KEY AUTOINCREMENT,
               name       TEXT NOT NULL,
               message    TEXT NOT NULL,
               created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
           )"""
    )
    empty = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0
    if empty and JSON_PATH.exists():
        try:
            items = json.loads(JSON_PATH.read_text(encoding="utf-8"))
            for it in items:
                db.execute(
                    "INSERT INTO entries (id, name, message, created_at) "
                    "VALUES (?, ?, ?, ?)",
                    (it["id"], it["name"], it["message"],
                     it.get("created_at", "")),
                )
            db.commit()
        except (json.JSONDecodeError, KeyError, sqlite3.Error) as e:
            print(f"[warn] Không đọc được data.json: {e}")
    db.close()


def fetch_entries():
    return get_db().execute(
        "SELECT * FROM entries ORDER BY id DESC"
    ).fetchall()


def save_json():
    """Ghi toàn bộ lời nhắn ra data.json (gọi sau mỗi lần thêm/xoá)."""
    rows = get_db().execute("SELECT * FROM entries ORDER BY id").fetchall()
    JSON_PATH.write_text(
        json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ------------------------------------------------------------------ Routes
@app.route("/")
def index():
    return render_template("index.html", entries=fetch_entries())


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()

        errors = []
        if not name:
            errors.append("Bạn chưa nhập tên.")
        elif len(name) > MAX_NAME:
            errors.append(f"Tên tối đa {MAX_NAME} ký tự.")
        if not message:
            errors.append("Bạn chưa nhập lời nhắn.")
        elif len(message) > MAX_MESSAGE:
            errors.append(f"Lời nhắn tối đa {MAX_MESSAGE} ký tự.")

        if errors:
            # render lại form, giữ nguyên nội dung đã gõ
            return render_template("add.html", errors=errors,
                                   name=name, message=message,
                                   max_name=MAX_NAME,
                                   max_message=MAX_MESSAGE), 400

        db = get_db()
        db.execute("INSERT INTO entries (name, message) VALUES (?, ?)",
                   (name, message))
        db.commit()
        save_json()
        flash("Đã gửi lời nhắn của bạn.")
        return redirect(url_for("index"))

    return render_template("add.html", errors=[], name="", message="",
                           max_name=MAX_NAME, max_message=MAX_MESSAGE)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    db = get_db()
    cur = db.execute("DELETE FROM entries WHERE id = ?", (id,))
    db.commit()
    if cur.rowcount:
        save_json()
        flash(f"Đã xoá lời nhắn #{id}.")
    else:
        flash(f"Không tìm thấy lời nhắn #{id}.")
    return redirect(url_for("index"))


@app.route("/stats")
def stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    top5 = db.execute(
        """SELECT name, COUNT(*) AS n FROM entries
           GROUP BY name ORDER BY n DESC, name ASC LIMIT 5"""
    ).fetchall()

    chart_ready = False
    if top5:
        names = [r["name"] for r in top5]
        counts = [r["n"] for r in top5]

        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=130)
        bars = ax.bar(names, counts, color="#1D3557", width=0.55)
        ax.bar_label(bars, padding=3, fontsize=10, color="#1D3557")
        ax.set_ylabel("Số lời nhắn")
        ax.set_ylim(0, max(counts) + 1)
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.spines[["top", "right"]].set_visible(False)
        plt.xticks(rotation=20, ha="right")
        fig.tight_layout()
        fig.savefig(CHART_PATH, transparent=False, facecolor="#FFFFFF")
        plt.close(fig)  # tránh rò rỉ bộ nhớ
        chart_ready = True

    return render_template("stats.html", total=total, top5=top5,
                           chart_ready=chart_ready, v=int(time.time()))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
