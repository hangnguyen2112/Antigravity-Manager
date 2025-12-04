# -*- coding: utf-8 -*-
import json
import os
import time
import uuid
from pathlib import Path
from datetime import datetime

# Use relative imports
from utils import info, error, warning, get_accounts_file_path, get_app_data_dir
from db_manager import backup_account, restore_account, get_current_account_info
from process_manager import close_antigravity, start_antigravity

def load_accounts():
    """Tải danh sách tài khoản"""
    file_path = get_accounts_file_path()
    if not file_path.exists():
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        error(f"Tải danh sách tài khoản thất bại: {e}")
        return {}

def save_accounts(accounts):
    """Lưu danh sách tài khoản"""
    file_path = get_accounts_file_path()
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        error(f"Lưu danh sách tài khoản thất bại: {e}")
        return False

def add_account_snapshot(name=None, email=None):
    """Thêm tài khoản mới từ trạng thái hiện tại, nếu email đã tồn tại thì sẽ ghi đè"""
    # 0. Tự động lấy thông tin
    if not email:
        info("Đang cố gắng đọc thông tin tài khoản từ cơ sở dữ liệu...")
        account_info = get_current_account_info()
        if account_info and "email" in account_info:
            email = account_info["email"]
            info(f"Đã tự động lấy được email: {email}")
        else:
            warning("Không thể tự động lấy email từ cơ sở dữ liệu, sẽ sử dụng 'Unknown'")
            email = "Unknown"
            
    if not name:
        # Nếu không cung cấp tên, sử dụng phần trước @ của email hoặc tên mặc định
        if email and email != "Unknown":
            name = email.split("@")[0]
        else:
            name = f"Account_{int(time.time())}"
        info(f"Sử dụng tên được tạo tự động: {name}")

    # 1. Kiểm tra xem đã tồn tại tài khoản với cùng email hay chưa
    accounts = load_accounts()
    existing_account = None
    existing_id = None
    
    for acc_id, acc_data in accounts.items():
        if acc_data.get("email") == email:
            existing_account = acc_data
            existing_id = acc_id
            break
    
    if existing_account:
        info(f"Phát hiện email {email} đã có bản sao lưu, sẽ ghi đè bản cũ")
        # Sử dụng ID và đường dẫn sao lưu hiện có
        account_id = existing_id
        backup_path = Path(existing_account["backup_file"])
        created_at = existing_account.get("created_at", datetime.now().isoformat())
        
        # Nếu không cung cấp tên mới, giữ lại tên cũ
        if not name or name == email.split("@")[0]:
            name = existing_account.get("name", name)
    else:
        info(f"Tạo bản sao lưu tài khoản mới: {email}")
        # Tạo ID mới và đường dẫn sao lưu
        account_id = str(uuid.uuid4())
        backup_filename = f"{account_id}.json"
        backup_dir = get_app_data_dir() / "backups"
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / backup_filename
        created_at = datetime.now().isoformat()
    
    # 2. Thực hiện sao lưu
    info(f"Đang sao lưu trạng thái hiện tại cho tài khoản: {name}")
    if not backup_account(email, str(backup_path)):
        error("Sao lưu thất bại, hủy thao tác thêm tài khoản")
        return False
    
    # 3. Cập nhật danh sách tài khoản
    accounts[account_id] = {
        "id": account_id,
        "name": name,
        "email": email,
        "backup_file": str(backup_path),
        "created_at": created_at,
        "last_used": datetime.now().isoformat()
    }
    
    if save_accounts(accounts):
        if existing_account:
            info(f"Bản sao lưu tài khoản {name} ({email}) đã được cập nhật")
        else:
            info(f"Tài khoản {name} ({email}) đã được thêm thành công")
        return True
    return False

def delete_account(account_id):
    """Xóa tài khoản"""
    accounts = load_accounts()
    if account_id not in accounts:
        error("Tài khoản không tồn tại")
        return False
    
    account = accounts[account_id]
    name = account.get("name", "Unknown")
    backup_file = account.get("backup_file")
    
    # Xóa tệp sao lưu
    if backup_file and os.path.exists(backup_file):
        try:
            os.remove(backup_file)
            info(f"Tệp sao lưu đã được xóa: {backup_file}")
        except Exception as e:
            warning(f"Xóa tệp sao lưu thất bại: {e}")
    
    # Xóa khỏi danh sách
    del accounts[account_id]
    if save_accounts(accounts):
        info(f"Tài khoản {name} đã được xóa")
        return True
    return False

def switch_account(account_id):
    """Chuyển sang tài khoản được chỉ định"""
    accounts = load_accounts()
    if account_id not in accounts:
        error("Tài khoản không tồn tại")
        return False
    
    account = accounts[account_id]
    name = account.get("name", "Unknown")
    backup_file = account.get("backup_file")
    
    if not backup_file or not os.path.exists(backup_file):
        error(f"Tệp sao lưu bị thiếu: {backup_file}")
        return False
    
    info(f"Chuẩn bị chuyển sang tài khoản: {name}")
    
    # 1. Đóng tiến trình
    if not close_antigravity():
        # Thử tiếp tục nhưng đưa ra cảnh báo
        warning("Không thể tắt Antigravity, thử khôi phục cưỡng bức...")
    
    # 2. Khôi phục dữ liệu
    if restore_account(backup_file):
        # Cập nhật thời gian sử dụng gần nhất
        accounts[account_id]["last_used"] = datetime.now().isoformat()
        save_accounts(accounts)
        
        # 3. Khởi động tiến trình
        start_antigravity()
        info(f"Chuyển sang tài khoản {name} thành công")
        return True
    else:
        error("Khôi phục dữ liệu thất bại")
        return False

def list_accounts_data():
    """Lấy dữ liệu danh sách tài khoản (dùng để hiển thị)"""
    accounts = load_accounts()
    data = list(accounts.values())
    # Sắp xếp giảm dần theo thời gian sử dụng gần nhất
    data.sort(key=lambda x: x.get("last_used", ""), reverse=True)
    return data
