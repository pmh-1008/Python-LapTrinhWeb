# Mô tả chi tiết dự án Python-LapTrinhWeb

## 1. Tổng quan

Đây là dự án web sổ lưu bút (Guestbook) viết bằng Python và Flask. Người dùng có thể để lại tên, lời nhắn, xem nội dung đã gửi, xóa lời nhắn và xem thống kê số lượt gửi theo tên.

Thư mục hiện tại chứa hai ứng dụng có thể chạy độc lập:

| Tiêu chí | Ứng dụng ở thư mục gốc | Ứng dụng trong `guestbook_vibe/` |
| --- | --- | --- |
| Giao diện | Danh sách lời nhắn dạng thẻ giấy màu | Bảng đen với giấy nhớ đặt theo tọa độ |
| Cách thêm | Nhập biểu mẫu rồi nhấn gửi | Chọn trang, nhập nội dung rồi nhấn lên bảng |
| Độ dài tên tối đa | 50 ký tự | 30 ký tự |
| Độ dài lời nhắn tối đa | 500 ký tự | 90 ký tự |
| Cơ sở dữ liệu | `guestbook.db` | `guestbook_vibe/sticky.db` |
| Thời gian tạo | Có trường `created_at` | Không có trường thời gian |
| Phân trang | Chưa có | Chia bảng thành nhiều trang |
| Dữ liệu bổ sung | Thời gian gửi | Trang, tọa độ, góc nghiêng và màu giấy |

Mỗi ứng dụng sử dụng bộ template, CSS và dữ liệu riêng. Chạy `app.py` ở thư mục gốc sẽ mở phiên bản sổ lưu bút, không tự chuyển sang phiên bản bảng giấy nhớ.

## 2. Công nghệ sử dụng

| Công nghệ | Vai trò |
| --- | --- |
| Python | Xử lý nghiệp vụ, dữ liệu và tạo biểu đồ |
| Flask, khai báo `Flask>=3.0` | Định tuyến HTTP, nhận biểu mẫu, render trang và chuyển hướng |
| Jinja2 thông qua Flask | Kế thừa template, lặp danh sách và hiển thị dữ liệu |
| SQLite, qua module `sqlite3` | Lưu trữ lời nhắn trong file cơ sở dữ liệu |
| JSON, qua module `json` | Xuất dữ liệu sau thao tác thêm/xóa và nạp dữ liệu ban đầu |
| Matplotlib, khai báo `matplotlib>=3.8` | Sinh biểu đồ cột dưới dạng ảnh PNG |
| HTML và CSS | Xây dựng bố cục, biểu mẫu và giao diện giấy nhớ |
| JavaScript thuần | Xác nhận xóa; ở bản bảng giấy nhớ còn xử lý tọa độ, xem trước và lật trang |
| Google Fonts | Cung cấp phông chữ cho giao diện |

Matplotlib sử dụng backend `Agg` để vẽ ra file trên máy chủ mà không cần cửa sổ đồ họa. Các thư viện `json`, `sqlite3`, `pathlib`, `time` và `random` thuộc thư viện chuẩn Python; không cần cài riêng bằng pip.

## 3. Cấu trúc thư mục

```text
Python-LapTrinhWeb/
├── DESCRIPTION.md             # Tài liệu mô tả chi tiết dự án
├── README.md                  # Hướng dẫn ngắn cho ứng dụng ở gốc
├── requirements.txt           # Phụ thuộc của ứng dụng ở gốc
├── app.py                     # Flask, xử lý SQLite/JSON và biểu đồ
├── guestbook.db               # Dữ liệu SQLite của sổ lưu bút
├── data.json                  # Bản xuất dữ liệu của sổ lưu bút
├── templates/
│   ├── base.html              # Khung trang và thanh điều hướng
│   ├── index.html             # Danh sách lời nhắn
│   ├── add.html               # Biểu mẫu thêm lời nhắn
│   └── stats.html             # Tổng số, top 5 và biểu đồ
├── static/
│   ├── style.css              # Giao diện sổ lưu bút
│   └── stats.png              # Ảnh biểu đồ được sinh từ dữ liệu
└── guestbook_vibe/
    ├── README.md              # Hướng dẫn bản bảng giấy nhớ
    ├── requirements.txt       # Phụ thuộc của bản bảng giấy nhớ
    ├── app.py                 # Flask và nghiệp vụ đặt giấy nhớ
    ├── sticky.db              # Dữ liệu SQLite của bảng giấy nhớ
    ├── data.json              # Bản xuất dữ liệu gồm vị trí giấy
    ├── templates/
    │   ├── base.html          # Khung bảng và điều hướng
    │   ├── index.html         # Hiển thị giấy nhớ và chuyển trang
    │   ├── add.html           # Chọn trang và vị trí để dán giấy
    │   └── stats.html         # Thống kê giấy nhớ
    └── static/
        └── style.css          # Giao diện bảng đen và giấy nhớ
```

Ở bản `guestbook_vibe`, file `static/stats.png` được tạo khi truy cập `/stats` và có dữ liệu thống kê. Nó có thể chưa tồn tại trước lần tạo biểu đồ đầu tiên.

## 4. Ứng dụng sổ lưu bút ở thư mục gốc

### 4.1. Trang chủ

Route `/` lấy toàn bộ lời nhắn theo `id` giảm dần, sau đó truyền biến `entries` vào `templates/index.html`. Lời nhắn có ID lớn hơn xuất hiện trước.

Mỗi thẻ hiển thị nội dung, tên người gửi, thời gian tạo, ID và nút xóa. Màu thẻ được xác định bằng `id % 4`, tương ứng bốn lớp CSS `c0` đến `c3`. Khi chưa có dữ liệu, trang hiển thị lời mời viết lời nhắn đầu tiên.

Giao diện dùng CSS Grid để tự bố trí các thẻ theo chiều rộng. Nội dung giữ xuống dòng và có thể ngắt chuỗi dài để hạn chế tràn thẻ. Phông `Be Vietnam Pro` dùng cho giao diện chung và `Patrick Hand` dùng cho lời nhắn.

### 4.2. Thêm lời nhắn

`GET /add` hiển thị biểu mẫu trống. `POST /add` đọc hai trường `name` và `message`, loại bỏ khoảng trắng ở hai đầu rồi kiểm tra:

- Tên bắt buộc và không vượt quá 50 ký tự.
- Lời nhắn bắt buộc và không vượt quá 500 ký tự.

Nếu dữ liệu không hợp lệ, máy chủ render lại biểu mẫu với mã HTTP `400`, danh sách lỗi và nội dung vừa nhập. Nếu hợp lệ, ứng dụng ghi SQLite, commit, xuất lại JSON, tạo thông báo bằng `flash()` rồi chuyển hướng về trang chủ.

Biểu mẫu có thuộc tính `maxlength`, nhưng việc kiểm tra trên máy chủ vẫn là bước quyết định dữ liệu có được lưu hay không. Thuộc tính `novalidate` cho phép luồng báo lỗi của ứng dụng xử lý việc gửi biểu mẫu.

### 4.3. Xóa lời nhắn

Nút xóa gửi `POST /delete/<id>` sau hộp thoại xác nhận của trình duyệt. Máy chủ xóa theo ID và commit. Nếu tìm thấy bản ghi, ứng dụng xuất lại JSON và thông báo đã xóa; nếu không tìm thấy, ứng dụng thông báo tương ứng. Cả hai trường hợp đều chuyển hướng về `/`.

### 4.4. Thống kê

Route `/stats` tính tổng số lời nhắn và lấy tối đa năm tên có nhiều lời nhắn nhất. Truy vấn nhóm theo giá trị `name`, sắp theo số lượng giảm dần rồi tên tăng dần khi bằng số lượng.

Khi có dữ liệu, Matplotlib vẽ biểu đồ cột và ghi vào `static/stats.png`. Sau khi lưu ảnh, figure được đóng bằng `plt.close(fig)`. Template thêm tham số thời gian `?v=...` vào URL ảnh để hạn chế trình duyệt dùng lại biểu đồ cũ. Khi chưa có dữ liệu, trang hiển thị trạng thái trống.

## 5. Ứng dụng bảng giấy nhớ trong guestbook_vibe

### 5.1. Bảng và giấy nhớ

Bảng có kích thước logic 960 × 600 px, mỗi giấy nhớ có kích thước 200 × 200 px. Giấy được đặt theo tọa độ `x`, `y`, góc nghiêng `rot` và lớp màu `paper0` đến `paper5`.

Trong một trang, dữ liệu được lấy theo ID tăng dần. Các giấy xuất hiện sau trong HTML nằm trên giấy trước, cho phép giấy chồng lên nhau. Khi người dùng chọn giấy, JavaScript bật trạng thái `lifted` để đưa giấy lên trên, làm thẳng và hiển thị nút xóa. Có thể dùng Enter hoặc Space khi giấy đang được focus để bật/tắt trạng thái này.

Trang chủ và trang thêm giấy tính tỉ lệ thu nhỏ theo chiều rộng khung chứa, với mức tối thiểu 55%. Khi màn hình quá hẹp, khung cho phép cuộn ngang.

### 5.2. Dán giấy mới

Luồng sử dụng gồm:

1. Mở `/add`.
2. Chọn một trang hiện có hoặc lựa chọn trang mới nếu đã có trang chứa giấy.
3. Nhập tên tối đa 30 ký tự và lời nhắn tối đa 90 ký tự.
4. Di chuyển chuột trên bảng để xem trước nội dung và vị trí giấy.
5. Nhấn lên bảng để gửi biểu mẫu ngay tại vị trí đó.

JavaScript chuyển tọa độ chuột về hệ tọa độ của bảng sau khi tính tỉ lệ thu nhỏ, rồi giới hạn vị trí để hình vuông giấy nằm trong bảng trước khi áp dụng góc nghiêng. Tọa độ được gửi qua hai trường ẩn `x` và `y`.

Máy chủ kiểm tra tên, lời nhắn, trang đích và giới hạn `0 ≤ x ≤ 760`, `0 ≤ y ≤ 400`. Nếu hợp lệ, ứng dụng tạo góc nghiêng ngẫu nhiên từ -5 đến 5 độ và chọn một trong sáu màu, sau đó lưu SQLite, xuất JSON và chuyển đến trang vừa dán.

### 5.3. Quản lý trang

Hàm `page_list()` lấy các giá trị trang đang có giấy. Trang không còn giấy sẽ không xuất hiện trong danh sách này. Nếu chưa có giấy nào, giao diện vẫn hiển thị bảng trống với trang mặc định 1.

Tham số `?page=` trên trang chủ là số thứ tự trang hiển thị trong danh sách hiện có; số này có thể khác giá trị `page` lưu trong cơ sở dữ liệu khi các trang ở giữa đã trống. Hàm `page_options()` ánh xạ nhãn hiển thị sang giá trị trang thực tế.

Người dùng chuyển trang bằng nút Trước/Sau hoặc phím mũi tên trái/phải. Trạng thái nhấc giấy chỉ thay đổi cách hiển thị trong trình duyệt, không cập nhật tọa độ trong SQLite.

## 6. Các route

Cả hai ứng dụng đều cung cấp các route nghiệp vụ sau; chúng trả về HTML hoặc chuyển hướng, chưa có API JSON riêng.

| Route | Phương thức | Chức năng |
| --- | --- | --- |
| `/` | GET | Xem lời nhắn; bản bảng giấy nhớ hỗ trợ `?page=` |
| `/add` | GET | Hiển thị giao diện thêm |
| `/add` | POST | Kiểm tra và lưu lời nhắn |
| `/delete/<int:id>` | POST | Xóa lời nhắn theo ID |
| `/stats` | GET | Xem tổng số, top 5 và biểu đồ |

Flask cũng phục vụ CSS và ảnh thông qua đường dẫn `/static/...`.

## 7. Mô hình dữ liệu

### 7.1. Bảng entries trong guestbook.db

| Trường | Kiểu SQLite | Ý nghĩa |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Mã lời nhắn tự tăng |
| `name` | TEXT NOT NULL | Tên người gửi |
| `message` | TEXT NOT NULL | Nội dung lời nhắn |
| `created_at` | TEXT NOT NULL | Mặc định từ `datetime('now', 'localtime')` |

Thời gian mặc định phụ thuộc giờ địa phương của môi trường chạy SQLite. Các giới hạn độ dài được kiểm tra trong Python; schema không khai báo ràng buộc độ dài tương ứng.

### 7.2. Bảng entries trong sticky.db

| Trường | Kiểu SQLite | Ý nghĩa |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | Mã giấy nhớ tự tăng |
| `name` | TEXT NOT NULL | Tên người gửi |
| `message` | TEXT NOT NULL | Nội dung giấy |
| `page` | INTEGER | Giá trị trang lưu trữ |
| `x`, `y` | REAL | Tọa độ góc trên trái của giấy |
| `rot` | REAL | Góc nghiêng theo độ |
| `color` | INTEGER | Chỉ số màu giấy |

### 7.3. Vai trò của JSON

SQLite là nguồn dữ liệu được truy vấn khi ứng dụng phục vụ yêu cầu. `data.json` là bản xuất toàn bộ bản ghi theo ID tăng dần, dùng UTF-8 và giữ nguyên ký tự tiếng Việt qua `ensure_ascii=False`.

Đây là cơ chế xuất dữ liệu sau thao tác, không phải đồng bộ hai chiều liên tục:

- Khi thêm/xóa, ứng dụng commit SQLite trước rồi mới ghi lại JSON.
- Sửa JSON khi SQLite đang có dữ liệu không tự cập nhật SQLite.
- `init_db()` chỉ nạp JSON nếu bảng đang trống và file JSON tồn tại.
- Nếu đã xóa hết bản ghi nhưng JSON vẫn chứa dữ liệu cũ, lần khởi tạo tiếp theo có thể nạp lại dữ liệu đó.
- Hai ứng dụng có schema khác nhau; không nên coi hai file JSON là hoàn toàn thay thế được cho nhau.

Bản bảng giấy nhớ có `fallback_spot()` để cấp trang và vị trí dạng lưới cho dữ liệu nhập thiếu thông tin vị trí. Đây là bước hỗ trợ dữ liệu cũ, không phải giới hạn 12 giấy mỗi trang trong thao tác sử dụng thông thường.

## 8. Tổ chức mã nguồn và luồng xử lý

`app.py` của mỗi ứng dụng kết hợp cấu hình, truy cập dữ liệu, route và tạo biểu đồ trong một module.

| Hàm | Vai trò |
| --- | --- |
| `get_db()` | Tạo hoặc dùng lại kết nối SQLite trong Flask `g` của ngữ cảnh hiện tại |
| `close_db()` | Đóng kết nối khi kết thúc ngữ cảnh ứng dụng |
| `init_db()` | Tạo bảng nếu chưa có và nạp JSON khi bảng trống |
| `save_json()` | Đọc toàn bộ bản ghi và xuất JSON |
| `index()` | Lấy dữ liệu để render trang chủ |
| `add()` | Nhận dữ liệu, kiểm tra và lưu lời nhắn |
| `delete()` | Xóa bản ghi và chuyển hướng |
| `stats()` | Truy vấn thống kê, tạo biểu đồ và render trang |

Bản gốc có thêm `fetch_entries()`. Bản bảng giấy nhớ có thêm `fallback_spot()`, `page_list()`, `page_options()` và `render_add()` để xử lý vị trí, trang và biểu mẫu.

Luồng thêm thành công: trình duyệt gửi POST → Flask kiểm tra dữ liệu → SQLite INSERT và commit → ghi JSON → chuyển hướng → trình duyệt GET trang chủ. Cách chuyển hướng sau POST giúp hạn chế gửi lặp khi tải lại trang kết quả.

Các đường dẫn DB, JSON và biểu đồ đều được tính từ vị trí `app.py` bằng `Path(__file__).resolve().parent`.

## 9. Cài đặt và chạy

Thực hiện các lệnh sau trong PowerShell tại thư mục gốc dự án. Cần có Python và pip hoạt động trên máy.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Chạy bản sổ lưu bút:

```powershell
.\.venv\Scripts\python.exe app.py
```

Hoặc chạy bản bảng giấy nhớ:

```powershell
.\.venv\Scripts\python.exe guestbook_vibe\app.py
```

Hai file `requirements.txt` hiện khai báo cùng phụ thuộc nên có thể dùng chung môi trường ảo. Mở `http://127.0.0.1:5000` cho bản sổ lưu bút hoặc `http://127.0.0.1:5001` cho bản bảng giấy nhớ. Nhấn Ctrl+C trong terminal để dừng.

Ứng dụng ở thư mục gốc dùng cổng 5000, ứng dụng trong `guestbook_vibe/` dùng cổng 5001. Có thể chạy đồng thời hai ứng dụng bằng hai terminal riêng. Khi chạy trực tiếp file `app.py` tương ứng, mỗi ứng dụng thực thi `init_db()` trước khi chạy Flask với `debug=True`.

Nếu khởi động bằng cách import module, chẳng hạn qua Flask CLI hoặc WSGI, khối `if __name__ == '__main__'` không chạy. Khi đó cần chủ động gọi `init_db()` trước khi nhận yêu cầu nếu cơ sở dữ liệu chưa được khởi tạo.

## 10. Phạm vi hiện tại và hướng mở rộng

Dự án phù hợp để thực hành routing, xử lý biểu mẫu, Jinja2, SQLite, xuất JSON, tạo biểu đồ và tương tác DOM.

Các điểm cần biết khi tiếp tục phát triển:

- Chưa có đăng nhập và phân quyền; các route xóa chưa kiểm tra quyền sở hữu lời nhắn.
- Biểu mẫu chưa có token CSRF. Hộp thoại xác nhận xóa là tương tác phía trình duyệt.
- Bản gốc dùng `secret_key` cố định trong mã nguồn và cả hai bản bật chế độ debug khi chạy trực tiếp; cần cấu hình lại nếu triển khai thực tế.
- Việc thống kê dựa trên chuỗi tên, không phải tài khoản xác thực. Những người dùng cùng tên được gộp chung.
- SQLite và JSON được ghi theo hai bước riêng; nếu ghi JSON lỗi sau commit, hai nơi có thể tạm thời không khớp.
- Biểu đồ dùng chung một file ảnh cho mỗi ứng dụng và được tạo lại khi mở trang thống kê có dữ liệu.
- Bản gốc chưa có tìm kiếm, chỉnh sửa nội dung hoặc phân trang danh sách. Bản bảng giấy nhớ chưa có thao tác kéo để lưu vị trí mới.
- Chưa có bộ kiểm thử tự động trong cấu trúc hiện tại. Có thể bổ sung kiểm thử cho xác thực biểu mẫu, thêm/xóa, nạp JSON và phân trang.
- Việc tải phông Google Fonts cần kết nối mạng; CSS có phông dự phòng để tiếp tục hiển thị khi không tải được phông ngoài.

Các hướng mở rộng phù hợp gồm tách lớp truy cập dữ liệu, đưa cấu hình vào biến môi trường, thêm tài khoản và quyền quản trị, tìm kiếm lời nhắn, kiểm thử tự động và cải thiện cơ chế sao lưu dữ liệu.
