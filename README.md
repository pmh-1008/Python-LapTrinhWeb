# Guestbook – phiên bản Vibe Code

Flask + SQLite, dữ liệu đồng bộ ra `data.json`, thống kê & biểu đồ bằng Matplotlib.

## Chạy
```bash
pip install -r requirements.txt
python app.py
```
Mở http://127.0.0.1:5000

## Routes
| Route | Method | Việc làm |
|---|---|---|
| `/` | GET | Hiển thị toàn bộ lời nhắn (biến `entries`) |
| `/add` | GET, POST | Form thêm; kiểm tra rỗng/quá dài; lỗi thì render lại form |
| `/delete/<int:id>` | POST | Xoá theo ID rồi redirect về `/` |
| `/stats` | GET | Tổng số, top 5 người gửi, biểu đồ cột `static/stats.png` |

## Lưu trữ
- DB chính: `guestbook.db` (SQLite).
- Mỗi lần thêm/xoá đều ghi lại `data.json`.
- Khi khởi động, nếu DB trống mà có `data.json` thì tự nạp lại.
