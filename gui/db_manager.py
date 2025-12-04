# -*- coding: utf-8 -*-
import sqlite3
import json
import os
from datetime import datetime

# Use relative imports
from utils import info, error, warning, debug, get_antigravity_db_paths

# Danh sách các khóa cần sao lưu
KEYS_TO_BACKUP = [
    "antigravityAuthStatus",
    "jetskiStateSync.agentManagerInitState",
]



def get_db_connection(db_path):
    """Lấy kết nối cơ sở dữ liệu"""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        error_msg = str(e)
        if "locked" in error_msg.lower():
            error(f"Cơ sở dữ liệu đang bị khóa: {e}")
            error("Gợi ý: Hãy đảm bảo ứng dụng Antigravity đã được tắt hoàn toàn")
        else:
            error(f"Kết nối cơ sở dữ liệu thất bại: {e}")
        return None
    except Exception as e:
        error(f"Xảy ra lỗi bất ngờ khi kết nối cơ sở dữ liệu: {e}")
        return None

def backup_account(email, backup_file_path):
    """Sao lưu dữ liệu tài khoản vào tệp JSON"""
    db_paths = get_antigravity_db_paths()
    if not db_paths:
        error("Không tìm thấy đường dẫn cơ sở dữ liệu Antigravity")
        return False
    
    db_path = db_paths[0]
    if not db_path.exists():
        error(f"Tệp cơ sở dữ liệu không tồn tại: {db_path}")
        return False
        
    info(f"Đang sao lưu dữ liệu từ cơ sở dữ liệu: {db_path}")
    conn = get_db_connection(db_path)
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        data_map = {}
        
        # 1. Trích xuất các khóa thông thường
        for key in KEYS_TO_BACKUP:
            cursor.execute("SELECT value FROM ItemTable WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                data_map[key] = row[0]
                debug(f"Sao lưu trường: {key}")
            else:
                debug(f"Trường không tồn tại: {key}")
        

        
        # 3. Thêm siêu dữ liệu
        data_map["account_email"] = email
        data_map["backup_time"] = datetime.now().isoformat()
        
        # 4. Ghi vào tệp
        with open(backup_file_path, 'w', encoding='utf-8') as f:
            json.dump(data_map, f, ensure_ascii=False, indent=2)
            
        info(f"Sao lưu thành công: {backup_file_path}")
        return True
        
    except sqlite3.Error as e:
        error(f"Lỗi truy vấn cơ sở dữ liệu: {e}")
        return False
    except Exception as e:
        error(f"Lỗi trong quá trình sao lưu: {e}")
        return False
    finally:
        conn.close()

def restore_account(backup_file_path):
    """Khôi phục dữ liệu tài khoản từ tệp JSON"""
    if not os.path.exists(backup_file_path):
        error(f"Tệp sao lưu không tồn tại: {backup_file_path}")
        return False
        
    try:
        with open(backup_file_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
    except Exception as e:
        error(f"Đọc tệp sao lưu thất bại: {e}")
        return False
        
    db_paths = get_antigravity_db_paths()
    if not db_paths:
        error("Không tìm thấy đường dẫn cơ sở dữ liệu Antigravity")
        return False
    
    # Thông thường có hai tệp cơ sở dữ liệu: state.vscdb và state.vscdb.backup
    # Cần khôi phục cả hai
    success_count = 0
    
    for db_path in db_paths:
        # Cơ sở dữ liệu chính
        if _restore_single_db(db_path, backup_data):
            success_count += 1
            
        # Cơ sở dữ liệu sao lưu (nếu tồn tại)
        backup_db_path = db_path.with_suffix('.vscdb.backup')
        if backup_db_path.exists():
            if _restore_single_db(backup_db_path, backup_data):
                success_count += 1
                
    return success_count > 0

def _restore_single_db(db_path, backup_data):
    """Khôi phục một tệp cơ sở dữ liệu"""
    if not db_path.exists():
        return False
        
    info(f"Đang khôi phục cơ sở dữ liệu: {db_path}")
    conn = get_db_connection(db_path)
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        restored_keys = []
        
        # 1. Khôi phục các khóa thông thường
        for key in KEYS_TO_BACKUP:
            if key in backup_data:
                value = backup_data[key]
                # Đảm bảo value là chuỗi
                if not isinstance(value, str):
                    value = json.dumps(value)
                    
                cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, value))
                restored_keys.append(key)
                debug(f"Khôi phục trường: {key}")

            
        conn.commit()
        info(f"Khôi phục cơ sở dữ liệu hoàn tất: {db_path}")
        return True
        
    except sqlite3.Error as e:
        error(f"Lỗi ghi cơ sở dữ liệu: {e}")
        return False
    except Exception as e:
        error(f"Lỗi trong quá trình khôi phục: {e}")
        return False
    finally:
        conn.close()


def get_current_account_info():
    """Trích xuất thông tin tài khoản hiện tại (email, v.v.) từ cơ sở dữ liệu"""
    db_paths = get_antigravity_db_paths()
    if not db_paths:
        return None
    
    db_path = db_paths[0]
    if not db_path.exists():
        return None
        
    conn = get_db_connection(db_path)
    if not conn:
        return None
        
    try:
        cursor = conn.cursor()
        
        # 1. Thử lấy từ antigravityAuthStatus
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("antigravityAuthStatus",))
        row = cursor.fetchone()
        if row:
            try:
                # Thử parse JSON
                data = json.loads(row[0])
                if isinstance(data, dict):
                    if "email" in data:
                        return {"email": data["email"]}
                    # Một số trường hợp có thể là token hoặc cấu trúc khác, duyệt đơn giản để tìm trường email
                    for k, v in data.items():
                        if k.lower() == "email" and isinstance(v, str):
                            return {"email": v}
            except:
                pass

        # 2. Thử lấy từ google.antigravity
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("google.antigravity",))
        row = cursor.fetchone()
        if row:
            try:
                data = json.loads(row[0])
                if isinstance(data, dict) and "email" in data:
                    return {"email": data["email"]}
            except:
                pass
                
        # 3. Thử lấy từ antigravityUserSettings.allUserSettings
        cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("antigravityUserSettings.allUserSettings",))
        row = cursor.fetchone()
        if row:
            try:
                data = json.loads(row[0])
                if isinstance(data, dict) and "email" in data:
                    return {"email": data["email"]}
            except:
                pass
                
        return None
        
    except Exception as e:
        error(f"Lỗi khi trích xuất thông tin tài khoản: {e}")
        return None
    finally:
        conn.close()
