# Guestbook – Sổ lưu bút

Dự án web sổ lưu bút sử dụng **Python, Flask và SQLite**, cho phép người dùng để lại lời nhắn và xem các lời nhắn đã được chia sẻ. Giao diện được xây dựng bằng HTML, CSS và Jinja2; biểu đồ thống kê được tạo bằng Matplotlib.

## Chức năng chính

- Hiển thị lời nhắn dạng thẻ giấy màu, lời nhắn mới nhất ở trên cùng.
- Thêm lời nhắn gồm tên người gửi và nội dung; kiểm tra dữ liệu trống và độ dài tối đa.
- Xóa lời nhắn sau khi xác nhận.
- Xem tổng số lời nhắn, top 5 tên gửi nhiều nhất và biểu đồ cột.

## Cách hoạt động

Trình duyệt gửi yêu cầu đến Flask. Ứng dụng đọc dữ liệu từ SQLite và kết hợp với template Jinja2 để trả về trang HTML. Khi người dùng gửi lời nhắn, máy chủ kiểm tra tên (tối đa 50 ký tự) và nội dung (tối đa 500 ký tự), lưu dữ liệu rồi chuyển về trang chủ.

Dữ liệu chính được lưu trong `guestbook.db`. Sau mỗi lần thêm hoặc xóa, ứng dụng xuất lại toàn bộ lời nhắn ra `data.json`. Khi khởi động bằng `python app.py`, nếu bảng dữ liệu trống và có file JSON thì ứng dụng nạp dữ liệu từ file này. Trang thống kê tổng hợp dữ liệu trong SQLite và dùng Matplotlib tạo ảnh biểu đồ tại `static/stats.png`.

## Cấu trúc chính

```text
├── app.py              # Ứng dụng Flask và xử lý dữ liệu
├── templates/          # Giao diện trang chủ, thêm lời nhắn và thống kê
├── static/             # CSS và ảnh biểu đồ
├── guestbook.db        # Cơ sở dữ liệu SQLite
├── data.json           # Bản xuất dữ liệu lời nhắn
├── requirements.txt    # Các thư viện cần cài đặt
├── guestbook_vibe/     # Phiên bản vibe code của dự án
└── DESCRIPTION.md      # Tài liệu mô tả chi tiết
```

## Cài đặt và chạy

Cần cài Python và pip. Tại thư mục gốc dự án, chạy:

```bash
python -m pip install -r requirements.txt
python app.py
```

Mở trình duyệt tại **http://127.0.0.1:5000**. Nhấn `Ctrl+C` trong terminal để dừng ứng dụng.

## Phiên bản vibe code: guestbook_vibe

`guestbook_vibe/` là phiên bản vibe code của dự án, trình bày lời nhắn dưới dạng giấy nhớ trên bảng đen. Người dùng chọn trang, nhập tên và lời nhắn rồi nhấn lên bảng để dán giấy tại vị trí mong muốn. Mỗi giấy có màu và góc nghiêng ngẫu nhiên; có thể nhấn vào giấy để xem rõ và xóa, hoặc chuyển giữa các trang bằng nút điều hướng và phím mũi tên.

Phiên bản này cũng sử dụng Flask, SQLite, JSON và Matplotlib, với dữ liệu riêng trong `guestbook_vibe/sticky.db` và `guestbook_vibe/data.json`. Để chạy từ thư mục gốc sau khi đã cài các thư viện:

```bash
python guestbook_vibe/app.py
```

Truy cập **http://127.0.0.1:5001**. Bản chính dùng cổng `5000`, bản vibe code dùng cổng `5001`; có thể chạy đồng thời hai phiên bản trong hai terminal riêng.

Xem thêm mô tả kỹ thuật trong [DESCRIPTION.md](DESCRIPTION.md).
