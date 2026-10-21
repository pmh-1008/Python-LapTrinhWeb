"""
Guestbook giấy nhớ - dán lên bảng đen
Flask + SQLite (+ data.json) + thống kê Matplotlib

Người dùng tự chọn TRANG và tự nhấn lên bảng để chọn chỗ dán.
Chạy:  python app.py   ->  http://127.0.0.1:5000
"""
import json
import random
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # vẽ ra file, không cần cửa sổ
import matplotlib.pyplot as plt
from flask import Flask, g, redirect, render_template, request, url_for

BASE = Path(__file__).resolve().parent
DB_FILE = BASE / "sticky.db"
JSON_FILE = BASE / "data.json"
CHART_FILE = BASE / "static" / "stats.png"

# Kích thước (px) của bảng và giấy nhớ; phải khớp với style.css
BOARD_W, BOARD_H, NOTE = 960, 600, 200

app = Flask(__name__)


# ---------- Database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()


def fallback_spot(i):
    """Vị trí xếp lưới (12 giấy/trang) cho giấy chưa có toạ độ,
    ví dụ khi nạp data.json từ phiên bản khác."""
    page, k = divmod(i, 12)
    return page + 1, 20 + (k % 4) * 230, 20 + (k // 4) * 190


def init_db():
    """Tạo bảng. Nếu DB trống mà có data.json thì nạp dữ liệu từ file."""
    db = sqlite3.connect(DB_FILE)
    db.execute("""CREATE TABLE IF NOT EXISTS entries (
                      id      INTEGER PRIMARY KEY AUTOINCREMENT,
                      name    TEXT NOT NULL,
                      message TEXT NOT NULL,
                      page INTEGER, x REAL, y REAL, rot REAL, color INTEGER)""")

    if db.execute("SELECT COUNT(*) FROM entries").fetchone()[0] == 0 \
            and JSON_FILE.exists():
        lost = 0
        for e in json.loads(JSON_FILE.read_text(encoding="utf-8")):
            if all(e.get(k) is not None for k in ("page", "x", "y", "color")):
                spot = (e["page"], e["x"], e["y"], e.get("rot") or 0, e["color"])
            else:
                spot = (*fallback_spot(lost), random.uniform(-5, 5),
                        random.randrange(5))
                lost += 1
            db.execute("INSERT INTO entries (id, name, message, page, x, y, "
                       "rot, color) VALUES (?,?,?,?,?,?,?,?)",
                       (e["id"], e["name"], e["message"], *spot))
    db.commit()
    db.close()


def save_json():
    rows = get_db().execute(
        "SELECT id, name, message, page, x, y, rot, color "
        "FROM entries ORDER BY id").fetchall()
    JSON_FILE.write_text(
        json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2),
        encoding="utf-8")


def page_list(db):
    """Các trang đang có giấy nhớ (trang trống tự biến mất)."""
    return [r[0] for r in db.execute(
        "SELECT DISTINCT page FROM entries ORDER BY page")]


# ---------- Trang chủ ----------
@app.route("/")
def index():
    db = get_db()
    pages = page_list(db) or [1]
    cur = min(max(request.args.get("page", 1, type=int), 1), len(pages))
    # thứ tự id tăng dần = thứ tự dán: giấy mới nằm trên giấy cũ
    entries = db.execute("SELECT * FROM entries WHERE page = ? ORDER BY id",
                         (pages[cur - 1],)).fetchall()
    return render_template("index.html", entries=entries,
                           cur=cur, total_pages=len(pages),
                           board_w=BOARD_W, board_h=BOARD_H, note=NOTE)


# ---------- Dán giấy nhớ ----------
def page_options(db):
    """Các trang có thể chọn: trang đang có giấy + 1 trang mới."""
    existing = page_list(db)
    if not existing:
        return [{"value": 1, "label": "Trang 1"}]
    opts = [{"value": p, "label": f"Trang {i}"}
            for i, p in enumerate(existing, 1)]
    return opts + [{"value": existing[-1] + 1, "label": "Trang mới"}]


def render_add(db, error=None, name="", message="", selected=None, status=200):
    options = page_options(db)
    values = [o["value"] for o in options]
    if selected not in values:
        selected = None
        idx = request.args.get("page", type=int)     # đi từ trang chủ sang
        existing = page_list(db)
        if idx and 1 <= idx <= max(len(existing), 1):
            selected = values[idx - 1]
    boards = {v: [dict(n) for n in db.execute(
        "SELECT name, message, x, y, rot, color FROM entries "
        "WHERE page = ? ORDER BY id", (v,))] for v in values}
    return render_template("add.html", name=name, message=message, error=error,
                           options=options, selected=selected, boards=boards,
                           board_w=BOARD_W, board_h=BOARD_H, note=NOTE), status


@app.route("/add", methods=["GET", "POST"])
def add():
    db = get_db()
    if request.method == "GET":
        return render_add(db)

    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()
    page = request.form.get("page", type=int)
    x, y = request.form.get("x", type=int), request.form.get("y", type=int)

    def fail(msg):
        return render_add(db, msg, name, message, page, 400)

    if not name or not message:
        return fail("Cần nhập cả tên và lời nhắn.")
    if len(name) > 30 or len(message) > 90:
        return fail("Tên tối đa 30 ký tự, lời nhắn tối đa 90 ký tự.")
    if page not in [o["value"] for o in page_options(db)]:
        return fail("Hãy chọn trang để dán.")
    if x is None or y is None or not (0 <= x <= BOARD_W - NOTE
                                      and 0 <= y <= BOARD_H - NOTE):
        return fail("Hãy nhấn lên bảng để chọn chỗ dán.")

    db.execute("INSERT INTO entries (name, message, page, x, y, rot, color) "
               "VALUES (?,?,?,?,?,?,?)",
               (name, message, page, x, y, random.uniform(-5, 5),
                random.randrange(6)))
    db.commit()
    save_json()
    # chuyển tới đúng trang chứa giấy vừa dán
    return redirect(url_for("index", page=page_list(db).index(page) + 1))


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    db = get_db()
    db.execute("DELETE FROM entries WHERE id = ?", (id,))
    db.commit()
    save_json()
    return redirect(url_for("index", page=request.args.get("page", 1, type=int)))


@app.route("/stats")
def stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    top5 = db.execute("""SELECT name, COUNT(*) AS n FROM entries
                         GROUP BY name ORDER BY n DESC, name LIMIT 5""").fetchall()

    if top5:
        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=120, facecolor="#2B4A3E")
        ax.set_facecolor("#2B4A3E")
        bars = ax.bar([r["name"] for r in top5], [r["n"] for r in top5],
                      color="#FFE680", width=0.5)
        ax.bar_label(bars, color="#F2EFE6", padding=3)
        ax.set_ylabel("Số lời nhắn", color="#F2EFE6")
        ax.tick_params(colors="#F2EFE6")
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.spines[["top", "right"]].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color("#F2EFE6")
        plt.xticks(rotation=20, ha="right")
        fig.tight_layout()
        fig.savefig(CHART_FILE, facecolor=fig.get_facecolor())
        plt.close(fig)

    return render_template("stats.html", total=total, top5=top5)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
