# Guestbook giấy nhớ

```bash
python -m pip install -r requirements.txt
python app.py
```
Mở http://127.0.0.1:5000

- Mỗi lời nhắn là một giấy nhớ 200x200 dán lên bảng 960x600. Ở trang /add người dùng PHẢI chọn trang (hoặc "Trang mới"), nhập tên + lời nhắn, rồi nhấn lên bảng: giấy được dán NGAY vào chỗ vừa nhấn (không có nút dán, không có dán ngẫu nhiên). Màu và độ nghiêng của giấy là ngẫu nhiên.
- Giấy được phép đè lên nhau tự do (không kiểm tra che khuất); giấy dán sau nằm trên giấy dán trước.
- Nhấn vào một giấy để nhấc nó lên trên cùng (thẳng lại, hiện nút Xoá); nhấn lại hoặc nhấn ra ngoài để đặt xuống.
- Lật trang bằng nút Trước/Sau hoặc phím ← →.
- DB: SQLite (`sticky.db`). Mỗi lần thêm/xoá ghi lại `data.json`; khởi động mà DB trống thì nạp từ `data.json`.
- Routes: `/`, `/add`, `/delete/<id>` (POST), `/stats`.
