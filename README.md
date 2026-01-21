# 🚀 Trình quản lý Antigravity

> **Công cụ đa tài khoản Antigravity hiện đại dành cho macOS & Windows**

Antigravity Manager là một công cụ hỗ trợ mạnh mẽ, được thiết kế để giải quyết hạn chế Antigravity không hỗ trợ chuyển đổi nhiều tài khoản một cách nguyên bản. Bằng cách quản lý trạng thái cấu hình của ứng dụng, nó cho phép bạn chuyển đổi tức thời giữa số lượng tài khoản gần như không giới hạn, đồng thời cung cấp cơ chế sao lưu tự động, quản lý tiến trình và giao diện quản lý trực quan.

---

## ✨ Tính năng chính

### 🛡️ An toàn và quản lý tài khoản
*   **Ảnh chụp tài khoản không giới hạn**: Tạo số lượng bản sao lưu tài khoản tùy ý, lưu toàn bộ thông tin đăng nhập, cấu hình người dùng và trạng thái cục bộ.
*   **Nhận diện thông minh**: Tự động đọc email và ID tài khoản hiện đang đăng nhập từ cơ sở dữ liệu, không cần nhập tay.
*   **Cơ chế sao lưu tự động**:
    *   **Sao lưu khi khởi động**: Mỗi lần chạy trình quản lý sẽ tự động sao lưu trạng thái hiện tại, tránh bị ghi đè ngoài ý muốn.
    *   **Sao lưu khi chuyển đổi**: Trước khi chuyển tài khoản sẽ tự động lưu lại trạng thái mới nhất của tài khoản hiện tại.
*   **Siêu dữ liệu chi tiết**: Ghi lại thời điểm tạo, thời điểm sử dụng gần nhất, email và ID duy nhất cho từng bản lưu.

### ⚡️ Trải nghiệm liền mạch
*   **Chuyển đổi một cú click**: Chỉ cần một lần nhấn để hoàn thành toàn bộ quy trình “tắt ứng dụng -> thay dữ liệu -> khởi động lại”.
*   **Bảo vệ tiến trình**:
    *   **Thoát thân thiện**: Ưu tiên dùng AppleScript (macOS) hoặc `taskkill` (Windows) để yêu cầu ứng dụng thoát bình thường, bảo vệ tính toàn vẹn dữ liệu.
    *   **Buộc dừng dự phòng**: Nếu ứng dụng treo, hệ thống tự động nâng cấp thành chiến lược buộc dừng để đảm bảo chuyển đổi thành công.
*   **Hỗ trợ đa nền tảng**: Tương thích tốt với macOS (Intel / Apple Silicon) và Windows 10/11.

### 🎨 Giao diện hiện đại
*   **Dựa trên Flet**: GUI hiệu năng cao dựa trên Flutter, phản hồi nhanh.
*   **Hòa nhập với hệ thống**: Tự động thích ứng với chế độ sáng/tối của hệ điều hành, mang lại trải nghiệm cửa sổ tự nhiên.
*   **Tối ưu tương tác**: Danh sách rõ ràng, nút thao tác trực quan và hộp thoại xác nhận thân thiện.

---

## 🛠️ Bắt đầu nhanh

### Yêu cầu môi trường
*   **Hệ điều hành**: macOS 10.15+ hoặc Windows 10+
*   **Python**: 3.10 hoặc mới hơn
*   **Antigravity**: Đã cài đặt và chạy ít nhất một lần

### 1. Cài đặt phụ thuộc
Tại thư mục gốc của dự án, cài đặt các gói cần thiết:

```bash
pip install -r requirements.txt
```

### 2. Chạy ứng dụng

#### 🖥️ Chế độ giao diện đồ họa (GUI) – khuyến nghị
Khởi động giao diện đồ họa để sử dụng đầy đủ tính năng:

```bash
# macOS / Linux
python gui/main.py

conda activate D:\conda\UAV-Image-stitching
# Windows
python gui\main.py
```

#### ⌨️ Chế độ dòng lệnh (CLI)
Phù hợp để tích hợp vào script hoặc cho người dùng thích dòng lệnh.

**Menu tương tác**:
```bash
python main.py
```

**Một số lệnh thường dùng**:
```bash
# Liệt kê tất cả bản lưu
python main.py list

# Sao lưu tài khoản hiện tại (tự động lấy tên)
python main.py add

# Sao lưu với tên chỉ định
python main.py add -n "tai_khoan_cong_viec"

# Chuyển tài khoản (dùng ID hoặc số thứ tự trong danh sách)
python main.py switch -i 1

# Xóa bản lưu
python main.py delete -i 1
```

---

## 📦 Đóng gói và triển khai

Dự án đã tích hợp sẵn script build tự động, có thể tạo ra các file thực thi độc lập không cần môi trường Python.

### 🍎 Đóng gói trên macOS
Build ứng dụng `.app` và gói cài đặt `.dmg`:

```bash
# 1. Cấp quyền thực thi cho script
chmod +x build_macos.sh

# 2. Chạy script build
./build_macos.sh
```
*   **Đường dẫn sản phẩm**: `gui/build/macos/`
*   **Bao gồm**: `Antigravity Manager.app`, `Antigravity Manager.dmg`
*   **Kiến trúc**: Universal Binary (hỗ trợ Intel & M1/M2/M3)

### 🪟 Đóng gói trên Windows
Build chương trình thực thi `.exe` một file:

```powershell
# Chạy trong PowerShell
./build_windows.ps1
```
*   **Đường dẫn sản phẩm**: `dist/`
*   **Bao gồm**: `Antigravity Manager.exe`
*   **Đặc điểm**: Không có cửa sổ console đen, một file duy nhất, dễ mang theo.

---

## 🧩 Kiến trúc kỹ thuật

### Cấu trúc thư mục
```
antigravity_manager/
├── assets/                 # Tài nguyên tĩnh (icon, v.v.)
├── gui/                    # Mã nguồn chính của GUI
│   ├── main.py             # Điểm vào GUI
│   ├── account_manager.py  # Logic tài khoản (thêm/xóa/sửa/đọc)
│   ├── process_manager.py  # Quản lý tiến trình (đa nền tảng)
│   ├── db_manager.py       # Truy cập dữ liệu (cơ sở dữ liệu/tệp)
│   ├── views/              # Các thành phần giao diện
│   └── utils.py            # Tiện ích dùng chung
├── main.py                 # Điểm vào CLI
├── build_macos.sh          # Script build cho macOS
├── build_windows.ps1       # Script build cho Windows
└── requirements.txt        # Các phụ thuộc Python
```

### Lưu trữ dữ liệu
*   **Tệp cấu hình**: `~/.antigravity-agent/accounts.json` (lưu chỉ mục danh sách tài khoản)
*   **Dữ liệu sao lưu**: `~/.antigravity-agent/backups/*.json` (các snapshot dữ liệu tài khoản)
*   **Tệp nhật ký**: `~/.antigravity-agent/app.log`

---

## ❓ Câu hỏi thường gặp (FAQ)

**Hỏi: Sau khi chuyển tài khoản, Antigravity không tự khởi động?**  
Đáp: Hãy đảm bảo Antigravity được cài ở đường dẫn tiêu chuẩn (trên macOS là `/Applications`, trên Windows là thư mục cài đặt mặc định). Nếu bạn dùng đường dẫn tùy chỉnh, chương trình sẽ cố gắng khởi động thông qua giao thức URI (`antigravity://`).

**Hỏi: Tệp sao lưu được lưu ở đâu?**  
Đáp: Tất cả dữ liệu được lưu trong thư mục `.antigravity-agent` trong thư mục home của người dùng. Bạn có thể sao lưu thủ công cả thư mục này bất cứ lúc nào.

**Hỏi: Tại sao trên Windows phần mềm diệt virus lại báo độc?**  
Đáp: Các file `.exe` một tệp được đóng gói bằng PyInstaller đôi khi bị nhận nhầm là mã độc – đây là vấn đề đã biết của PyInstaller. Bạn có thể cho ứng dụng vào danh sách tin cậy hoặc chạy trực tiếp từ mã nguồn Python.

---

## 📄 Giấy phép

Dự án sử dụng giấy phép MIT. Rất hoan nghênh mọi Issue và Pull Request.

Copyright (c) 2025 Ctrler.
