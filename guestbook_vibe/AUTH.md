# Đăng nhập tùy chọn và quyền xóa

Khách vẫn có thể đăng note mà không cần tài khoản. Đăng ký tại `/register`, đăng nhập tại `/login`. Mật khẩu được lưu dưới dạng hash; tài khoản đăng ký qua web luôn là người dùng thường.

- Admin xóa được mọi note.
- Người dùng thường xóa được note gắn với tài khoản của mình trên mọi trình duyệt sau khi đăng nhập.
- Note đăng khi là khách được nhận diện bằng cookie của trình duyệt, kể cả sau khi đăng nhập hoặc đăng xuất. Xóa cookie, đổi trình duyệt hoặc cookie hết hạn sẽ mất quyền xóa note khách. Cookie có thời hạn 31 ngày và được gia hạn khi truy cập.
- Note cũ chưa có thông tin sở hữu chỉ admin xóa được. Trùng tên hiển thị không cấp quyền xóa.

Tạo admin từ terminal ở thư mục gốc dự án (lệnh sẽ hỏi mật khẩu và xác nhận, không có mật khẩu mặc định):

```powershell
python -m flask --app guestbook_vibe.app create-admin admin
python guestbook_vibe/app.py
```

Ứng dụng tự thêm bảng tài khoản và cột chủ sở hữu khi chạy `init_db()`, giữ lại note hiện có. Nếu chạy bằng Flask CLI/WSGI, gọi `init_db()` trước khi phục vụ; lệnh `create-admin` cũng thực hiện bước này.

Khóa ký cookie lấy từ biến môi trường `GUESTBOOK_SECRET_KEY` hoặc khóa ngẫu nhiên lưu trong SQLite để phiên còn hiệu lực sau khi khởi động lại. Không công khai cơ sở dữ liệu vì có khóa ký và hash mật khẩu. JSON chỉ xuất nội dung note; không chứa thông tin chủ sở hữu hay tài khoản. Sao lưu SQLite để giữ tài khoản và quyền sở hữu; khôi phục chỉ từ JSON sẽ tạo note không có chủ sở hữu.

Mọi biểu mẫu POST có token CSRF; máy chủ kiểm tra quyền trước khi xóa, kể cả khi gửi yêu cầu trực tiếp.

Chạy kiểm thử trên cơ sở dữ liệu tạm:

```powershell
python -m unittest discover -s guestbook_vibe -p test_auth.py -v
```
