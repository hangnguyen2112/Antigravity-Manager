# -*- coding: utf-8 -*-
import os
import time
import platform
import subprocess
import psutil

# Use relative imports
from utils import info, error, warning, get_antigravity_executable_path, open_uri

def is_process_running(process_name=None):
    """Kiểm tra tiến trình Antigravity có đang chạy hay không
    
    Sử dụng phương thức kiểm tra đa nền tảng:
    - macOS: Kiểm tra đường dẫn chứa Antigravity.app
    - Windows: Kiểm tra tên tiến trình hoặc đường dẫn chứa antigravity
    - Linux: Kiểm tra tên tiến trình hoặc đường dẫn chứa antigravity
    """
    system = platform.system()
    
    for proc in psutil.process_iter(['name', 'exe']):
        try:
            process_name_lower = proc.info['name'].lower() if proc.info['name'] else ""
            exe_path = proc.info.get('exe', '').lower() if proc.info.get('exe') else ""
            
            # Kiểm tra đa nền tảng
            is_antigravity = False
            
            if system == "Darwin":
                # macOS: kiểm tra đường dẫn chứa Antigravity.app
                is_antigravity = 'antigravity.app' in exe_path
            elif system == "Windows":
                # Windows: kiểm tra tên tiến trình hoặc đường dẫn chứa antigravity
                is_antigravity = (process_name_lower in ['antigravity.exe', 'antigravity'] or 
                                 'antigravity' in exe_path)
            else:
                # Linux: kiểm tra tên tiến trình hoặc đường dẫn chứa antigravity
                is_antigravity = (process_name_lower == 'antigravity' or 
                                 'antigravity' in exe_path)
            
            if is_antigravity:
                return True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def close_antigravity(timeout=10, force_kill=True):
    """Đóng tất cả tiến trình Antigravity một cách thân thiện
    
    Chiến lược đóng (ba giai đoạn, đa nền tảng):
    1. Cách thoát thân thiện theo từng nền tảng
       - macOS: AppleScript
       - Windows: taskkill /IM (thoát nhẹ nhàng)
       - Linux: SIGTERM
    2. Kết thúc nhẹ nhàng (SIGTERM/TerminateProcess) - cho tiến trình thời gian dọn dẹp
    3. Buộc dừng (SIGKILL/taskkill /F) - phương án cuối cùng
    """
    info("Đang cố gắng đóng Antigravity...")
    system = platform.system()
    
    # Platform check
    if system not in ["Darwin", "Windows", "Linux"]:
        warning(f"Nền tảng hệ thống không xác định: {system}, sẽ thử phương pháp chung")
    
    try:
        # Giai đoạn 1: thoát thân thiện đặc thù theo từng nền tảng
        if system == "Darwin":
            # macOS: sử dụng AppleScript
            info("Đang thử thoát Antigravity bằng AppleScript...")
            try:
                result = subprocess.run(
                    ["osascript", "-e", 'tell application "Antigravity" to quit'],
                    capture_output=True,
                    timeout=3
                )
                if result.returncode == 0:
                    info("Đã gửi yêu cầu thoát, chờ ứng dụng phản hồi...")
                    time.sleep(2)
            except Exception as e:
                warning(f"Thoát bằng AppleScript thất bại: {e}, sẽ sử dụng cách khác")
        
        elif system == "Windows":
            # Windows: sử dụng taskkill để thoát nhẹ nhàng (không có tham số /F)
            info("Đang thử thoát Antigravity bằng taskkill...")
            try:
                # CREATE_NO_WINDOW = 0x08000000
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                result = subprocess.run(
                    ["taskkill", "/IM", "Antigravity.exe", "/T"],
                    capture_output=True,
                    timeout=3,
                    creationflags=0x08000000
                )
                if result.returncode == 0:
                    info("Đã gửi yêu cầu thoát, chờ ứng dụng phản hồi...")
                    time.sleep(2)
            except Exception as e:
                warning(f"Thoát bằng taskkill thất bại: {e}, sẽ sử dụng cách khác")
        
        # Linux không cần xử lý đặc biệt, dùng trực tiếp SIGTERM
        
        # Kiểm tra và thu thập các tiến trình vẫn đang chạy
        target_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_name_lower = proc.info['name'].lower() if proc.info['name'] else ""
                exe_path = proc.info.get('exe', '').lower() if proc.info.get('exe') else ""
                
                # Loại trừ tiến trình của chính ứng dụng
                if proc.pid == os.getpid():
                    continue
                
                # Loại trừ mọi tiến trình trong cùng thư mục với ứng dụng (tránh dừng nhầm chính mình và các tiến trình con)
                # Trong môi trường đóng gói PyInstaller, sys.executable trỏ tới file exe
                # Trong môi trường phát triển, nó trỏ tới python.exe
                try:
                    import sys
                    current_exe = sys.executable
                    current_dir = os.path.dirname(os.path.abspath(current_exe)).lower()
                    if exe_path and current_dir in exe_path:
                        # print(f"DEBUG: Skipping process in current dir: {proc.info['name']}")
                        continue
                except:
                    pass

                # Kiểm tra đa nền tảng: kiểm tra tên tiến trình hoặc đường dẫn thực thi
                is_antigravity = False
                
                if system == "Darwin":
                    # macOS: kiểm tra đường dẫn chứa Antigravity.app
                    is_antigravity = 'antigravity.app' in exe_path
                elif system == "Windows":
                    # Windows: khớp chính xác tên tiến trình antigravity.exe
                    # hoặc đường dẫn chứa antigravity và tên tiến trình không phải Antigravity Manager.exe
                    is_target_name = process_name_lower in ['antigravity.exe', 'antigravity']
                    is_in_path = 'antigravity' in exe_path
                    is_manager = 'manager' in process_name_lower
                    
                    is_antigravity = is_target_name or (is_in_path and not is_manager)
                else:
                    # Linux: kiểm tra tên tiến trình hoặc đường dẫn chứa antigravity
                    is_antigravity = (process_name_lower == 'antigravity' or 
                                     'antigravity' in exe_path)
                
                if is_antigravity:
                    info(f"Đã phát hiện tiến trình mục tiêu: {proc.info['name']} ({proc.pid}) - {exe_path}")
                    target_processes.append(proc)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not target_processes:
            info("Tất cả tiến trình Antigravity đã được đóng bình thường")
            return True
        
        info(f"Phát hiện {len(target_processes)} tiến trình vẫn đang chạy")

        # Giai đoạn 2: gửi tín hiệu kết thúc tiến trình (SIGTERM)
        info("Gửi tín hiệu kết thúc (SIGTERM)...")
        for proc in target_processes:
            try:
                if proc.is_running():
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                continue
            except Exception as e:
                continue

        # Chờ tiến trình thoát tự nhiên
        info(f"Chờ tiến trình thoát (tối đa {timeout} giây)...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            still_running = []
            for proc in target_processes:
                try:
                    if proc.is_running():
                        still_running.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not still_running:
                info("Tất cả tiến trình Antigravity đã được đóng bình thường")
                return True
                
            time.sleep(0.5)

        # Giai đoạn 3: buộc dừng các tiến trình cứng đầu (SIGKILL)
        if still_running:
            still_running_names = ", ".join([f"{p.info['name']}({p.pid})" for p in still_running])
            warning(f"Vẫn còn {len(still_running)} tiến trình chưa thoát: {still_running_names}")
            
            if force_kill:
                info("Gửi tín hiệu buộc dừng (SIGKILL)...")
                for proc in still_running:
                    try:
                        if proc.is_running():
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Kiểm tra lần cuối
                time.sleep(1)
                final_check = []
                for proc in still_running:
                    try:
                        if proc.is_running():
                            final_check.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not final_check:
                    info("Tất cả tiến trình Antigravity đã bị buộc dừng")
                    return True
                else:
                    final_list = ", ".join([f"{p.info['name']}({p.pid})" for p in final_check])
                    error(f"Không thể dừng các tiến trình: {final_list}")
                    return False
            else:
                error("Một số tiến trình không thể đóng, vui lòng đóng thủ công rồi thử lại")
                return False
                
        return True

    except Exception as e:
        error(f"Xảy ra lỗi khi đóng tiến trình Antigravity: {str(e)}")
        return False

def start_antigravity(use_uri=True):
    """Khởi động Antigravity
    
    Args:
        use_uri: Có sử dụng giao thức URI để khởi động hay không (mặc định True)
                 Giao thức URI đáng tin cậy hơn, không cần tìm đường dẫn tệp thực thi
    """
    info("Đang khởi động Antigravity...")
    system = platform.system()
    
    try:
        # Ưu tiên sử dụng giao thức URI để khởi động (dùng chung cho nhiều nền tảng)
        if use_uri:
            info("Khởi động bằng giao thức URI...")
            uri = "antigravity://oauth-success"
            
            if open_uri(uri):
                info("Lệnh khởi động Antigravity bằng URI đã được gửi")
                return True
            else:
                warning("Khởi động bằng URI thất bại, sẽ thử dùng đường dẫn tệp thực thi...")
                # Tiếp tục thực hiện phương án dự phòng bên dưới
        
        # Phương án dự phòng: sử dụng đường dẫn tệp thực thi để khởi động
        info("Khởi động bằng đường dẫn tệp thực thi...")
        if system == "Darwin":
            subprocess.Popen(["open", "-a", "Antigravity"])
        elif system == "Windows":
            path = get_antigravity_executable_path()
            if path and path.exists():
                # CREATE_NO_WINDOW = 0x08000000
                subprocess.Popen([str(path)], creationflags=0x08000000)
            else:
                error("Không tìm thấy tệp thực thi Antigravity")
                warning("Gợi ý: Có thể thử khởi động bằng giao thức URI (use_uri=True)")
                return False
        elif system == "Linux":
            subprocess.Popen(["antigravity"])
        
        info("Lệnh khởi động Antigravity đã được gửi")
        return True
    except Exception as e:
        error(f"Lỗi khi khởi động tiến trình: {e}")
        # Nếu khởi động bằng URI thất bại, thử dùng đường dẫn tệp thực thi
        if use_uri:
            warning("Khởi động bằng URI thất bại, thử dùng đường dẫn tệp thực thi...")
            return start_antigravity(use_uri=False)
        return False
