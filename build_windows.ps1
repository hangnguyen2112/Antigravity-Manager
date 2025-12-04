# build_windows.ps1

Write-Host "🚀 Bắt đầu build Trình quản lý Antigravity (Windows)..." -ForegroundColor Cyan

# 1. Kiểm tra môi trường
if (-not (Get-Command "flet" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Không tìm thấy lệnh flet, đang cài đặt..." -ForegroundColor Yellow
    pip install flet
}
if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Không tìm thấy lệnh pyinstaller, đang cài đặt..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Cài đặt phụ thuộc của dự án
if (Test-Path "requirements.txt") {
    Write-Host "📦 Đang cài đặt/cập nhật các phụ thuộc của dự án..." -ForegroundColor Green
    pip install -r requirements.txt
}

# 2. Dọn dẹp kết quả build cũ
Write-Host "🧹 Đang dọn dẹp các tệp build cũ..." -ForegroundColor Green
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

# 3. Chuẩn bị tài nguyên
# Đảm bảo gui/assets tồn tại và là bản mới nhất
Write-Host "📦 Đang đồng bộ tệp tài nguyên..." -ForegroundColor Green
if (-not (Test-Path "gui/assets")) { New-Item -ItemType Directory -Path "gui/assets" | Out-Null }
Copy-Item "assets/*" "gui/assets/" -Recurse -Force

# 4. Thực hiện build
Write-Host "🔨 Bắt đầu biên dịch..." -ForegroundColor Green

# Giai đoạn tiếp theo: đóng gói bằng PyInstaller

# 4. Thực hiện đóng gói PyInstaller
Write-Host "📦 Đang đóng gói..." -ForegroundColor Yellow

# Sử dụng PyInstaller để đóng gói trực tiếp
# --onefile: Đóng gói thành một tệp duy nhất
# --windowed: Không có console (ứng dụng GUI)
# --add-data: Thêm tệp tài nguyên (định dạng: đường_dẫn_nguồn;đường_dẫn_đích)
# --hidden-import: Ép buộc import các module có thể bị bỏ sót
pyinstaller --noconfirm --onefile --windowed --clean `
    --name "Antigravity Manager" `
    --icon "assets/icon.ico" `
    --add-data "assets;assets" `
    --add-data "gui;gui" `
    --noconsole `
    --paths "gui" `
    --hidden-import "views" `
    --hidden-import "views.home_view" `
    --hidden-import "views.settings_view" `
    --hidden-import "account_manager" `
    --hidden-import "db_manager" `
    --hidden-import "process_manager" `
    --hidden-import "utils" `
    --hidden-import "theme" `
    --hidden-import "icons" `
    "gui/main.py"

# Kiểm tra kết quả
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Đóng gói thất bại!" -ForegroundColor Red
    exit 1
}

# 5. Kiểm tra kết quả
if (Test-Path "dist/Antigravity Manager.exe") {
    Write-Host "`n🎉 Build thành công!" -ForegroundColor Green
    Write-Host "Vị trí tệp: dist/Antigravity Manager.exe" -ForegroundColor Cyan
} else {
    Write-Host "❌ Không tìm thấy tệp exe được tạo" -ForegroundColor Red
    exit 1
}
