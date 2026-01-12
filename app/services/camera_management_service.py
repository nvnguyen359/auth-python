# app/services/camera_management_service.py
import platform
import subprocess
import re
import time
import os 
import sys
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Thư viện cho việc quét cơ bản trên Windows/Mac
try:
    from cv2 import VideoCapture 
except ImportError:
    VideoCapture = None 

# --- IMPORT THỰC TẾ ---
from app.crud.camera_crud import camera_crud 
from app.db.schemas import CameraOut as CameraResponse 


# ----------------------------------------------------------------------
# 1. Định nghĩa Schemas
# ----------------------------------------------------------------------
class CameraScanInfo(BaseModel):
    name: str = Field(..., description="Tên hiển thị của camera")
    unique_id: str = Field(..., description="ID duy nhất") 
    device_id: str = Field(..., description="ID thiết bị")
    status: str = Field(..., pattern="^(ACTIVE|DISCONNECTED|ERROR)$")
    os_index: Optional[int] = Field(None)
    is_connected: bool = Field(False)


# ----------------------------------------------------------------------
# 2. Logic Phát hiện Camera (Đã thêm chặn log lỗi)
# ----------------------------------------------------------------------

def _get_linux_cameras() -> Dict[str, Dict[str, Any]]:
    cameras = {}
    try:
        result_find = subprocess.run(
            "ls -l /dev/video*", shell=True, capture_output=True, text=True, check=False
        )
        video_devices = [line.split()[-1] for line in result_find.stdout.splitlines() if '/dev/video' in line]
    except Exception:
        return {}
    
    for device_path in video_devices:
        try:
            cmd_info = f"v4l2-ctl -d {device_path} --info"
            result_info = subprocess.run(
                cmd_info, shell=True, capture_output=True, text=True, check=True, timeout=3
            )
            match = re.search(r'Card type\s*:\s*(.*)', result_info.stdout)
            name = match.group(1).strip() if match else f"Unknown Camera ({device_path})"
            os_index = int(device_path.replace('/dev/video', ''))
            
            cameras[device_path] = {
                'name': name,
                'os_index': os_index
            }
        except Exception:
            continue
    return cameras

def _get_other_os_cameras() -> Dict[str, Dict[str, Any]]:
    if VideoCapture is None:
        print("Cảnh báo: OpenCV (cv2) không được cài đặt.")
        return {}
        
    cameras = {}

    # --- CLASS HELPPER ĐỂ CHẶN OUTPUT RÁC TỪ C++ ---
    class SilenceStderr:
        def __enter__(self):
            try:
                # Lưu lại file descriptor gốc của stderr (thường là 2)
                self.fd = sys.stderr.fileno()
                self.dup_fd = os.dup(self.fd)
                # Mở 'devnull' (thùng rác hệ thống)
                self.devnull = os.open(os.devnull, os.O_WRONLY)
                # Chuyển hướng stderr sang devnull
                os.dup2(self.devnull, self.fd)
                os.close(self.devnull)
            except Exception:
                # Nếu môi trường không hỗ trợ (ví dụ debug mode), bỏ qua
                self.fd = None

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.fd is not None:
                # Khôi phục lại stderr gốc
                os.dup2(self.dup_fd, self.fd)
                os.close(self.dup_fd)

    # Dùng context manager bao quanh vòng lặp gây ồn ào
    with SilenceStderr():
        for i in range(10): 
            # Dòng VideoCapture này gây ra lỗi "index out of range" ở tầng C++
            cap = VideoCapture(i)
            if cap.isOpened():
                device_id_temp = f"Index_{i}" 
                cameras[device_id_temp] = {
                    'name': f"Camera Index {i}",
                    'os_index': i
                }
                cap.release()
            
    return cameras


def get_connected_cameras() -> Dict[str, Dict[str, Any]]:
    current_os = platform.system()
    if current_os == 'Linux':
        return _get_linux_cameras()
    elif current_os == 'Windows' or current_os == 'Darwin':
        return _get_other_os_cameras()
    else:
        return {}


# ----------------------------------------------------------------------
# 3. Camera Management Service
# ----------------------------------------------------------------------

class CameraManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.camera_crud = camera_crud 

    def upsert_camera_list(self) -> List[CameraResponse]:
        connected_cameras = get_connected_cameras()
        db_cameras_list = self.camera_crud.get_all(self.db)
        
        connected_ids = set(connected_cameras.keys())
        updated_cameras: List[CameraResponse] = []
        
        # Xử lý Camera cũ
        for db_camera in db_cameras_list:
            db_id = str(db_camera.device_id) 
            if db_id in connected_ids:
                new_info = connected_cameras[db_id]
                camera_data = {
                    'name': new_info['name'],
                    'unique_id': db_id,
                    'device_id': db_id,
                    'status': 'ACTIVE',
                    'is_connected': 1,
                    'os_index': new_info['os_index'],
                    'device_path': db_id
                }
                updated_db_camera = self.camera_crud.upsert(self.db, camera_data)
                updated_cameras.append(CameraResponse.from_orm(updated_db_camera))
                connected_ids.remove(db_id)
            else:
                if db_camera.status == "ACTIVE":
                    camera_data = {
                        'device_id': db_id, 
                        'status': 'DISCONNECTED',
                        'is_connected': 0,
                    }
                    updated_db_camera = self.camera_crud.upsert(self.db, camera_data)
                    updated_cameras.append(CameraResponse.from_orm(updated_db_camera))
                else:
                    updated_cameras.append(CameraResponse.from_orm(db_camera))

        # Xử lý Camera mới
        for new_id in connected_ids:
            new_info = connected_cameras[new_id]
            new_camera_data = {
                'name': new_info['name'],
                'unique_id': new_id,
                'device_id': new_id, 
                'status': 'ACTIVE',
                'is_connected': 1,
                'os_index': new_info['os_index'],
                'device_path': new_id
            }
            new_db_camera = self.camera_crud.upsert(self.db, new_camera_data)
            updated_cameras.append(CameraResponse.from_orm(new_db_camera))
            
        return updated_cameras


# ----------------------------------------------------------------------
# 4. Vòng lặp chạy ngầm
# ----------------------------------------------------------------------

def run_camera_upsert_loop(db_session_factory: Any, interval_seconds: int = 5):
    print(f"Camera Management Service started (interval: {interval_seconds}s)")
    while True:
        db = None
        try:
            db: Session = next(db_session_factory())
            service = CameraManagementService(db)
            
            updated_list = service.upsert_camera_list()
            active_count = len([c for c in updated_list if c.status == 'ACTIVE'])
            # Chỉ in log nếu có thay đổi hoặc muốn debug (để đỡ spam console)
            # print(f"[{time.strftime('%H:%M:%S')}] Camera list updated. Total: {len(updated_list)}, Active: {active_count}")

        except Exception as e:
            print(f"ERROR in Camera Management Loop: {e}")
        finally:
            if db:
                db.close()
        time.sleep(interval_seconds)