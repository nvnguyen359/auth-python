import platform
import subprocess
import re
import time
import threading
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ValidationError

# Thư viện cho việc quét cơ bản trên Windows/Mac
# Lưu ý: Cần đảm bảo thư viện 'opencv-python' đã được cài đặt.
try:
    from cv2 import VideoCapture 
except ImportError:
    VideoCapture = None 

# --- IMPORT THỰC TẾ ---
from app.crud.camera_crud import camera_crud 
from app.db import models, schemas 
# Sử dụng alias rõ ràng để tránh xung đột tên với mô hình Pydantic cục bộ
from app.db.schemas import CameraOut as CameraResponse # CameraResponse là Pydantic Model để trả về


# ----------------------------------------------------------------------
# 1. Định nghĩa Schemas cho Dữ liệu Quét (Dùng thay cho CameraBase bị ghi đè)
# ----------------------------------------------------------------------

# Model này chỉ dùng để định dạng dữ liệu quét được từ OS, 
# không liên quan đến việc chuyển đổi ORM ở cuối hàm.
class CameraScanInfo(BaseModel):
    """Schema cho dữ liệu camera được quét từ hệ điều hành."""
    name: str = Field(..., description="Tên hiển thị của camera")
    unique_id: str = Field(..., description="ID duy nhất (cột NOT NULL trong DB)") 
    device_id: str = Field(..., description="ID thiết bị (cột UNIQUE NOT NULL trong DB)")
    status: str = Field(..., pattern="^(ACTIVE|DISCONNECTED|ERROR)$")
    os_index: Optional[int] = Field(None, description="Chỉ số hệ thống (0, 1, 2...).")
    is_connected: bool = Field(False, description="Đang được cắm vào hệ thống (True/False)")


# ----------------------------------------------------------------------
# 2. Logic Phát hiện Camera Đa nền tảng (Giữ nguyên logic quét)
# ----------------------------------------------------------------------

def _get_linux_cameras() -> Dict[str, Dict[str, Any]]:
    cameras = {}
    try:
        # 1. Lấy danh sách thiết bị video
        result_find = subprocess.run(
            "ls -l /dev/video*", shell=True, capture_output=True, text=True, check=False
        )
        video_devices = [line.split()[-1] for line in result_find.stdout.splitlines() if '/dev/video' in line]
    except Exception:
        return {}
    
    for device_path in video_devices:
        try:
            # 2. Lấy thông tin chi tiết bằng v4l2-ctl
            cmd_info = f"v4l2-ctl -d {device_path} --info"
            result_info = subprocess.run(
                cmd_info, shell=True, capture_output=True, text=True, check=True, timeout=3
            )
            match = re.search(r'Card type\s*:\s*(.*)', result_info.stdout)
            name = match.group(1).strip() if match else f"Unknown Camera ({device_path})"
            os_index = int(device_path.replace('/dev/video', ''))
            
            # Key của dict là device_id/unique_id được sử dụng để tra cứu
            cameras[device_path] = {
                'name': name,
                'os_index': os_index
            }
        except Exception:
            continue
            
    return cameras

def _get_other_os_cameras() -> Dict[str, Dict[str, Any]]:
    if VideoCapture is None:
        print("Cảnh báo: OpenCV (cv2) không được cài đặt, không thể quét camera trên Windows/Mac.")
        return {}
        
    cameras = {}
    for i in range(10): 
        # Cố gắng mở camera theo index
        cap = VideoCapture(i)
        if cap.isOpened():
            # Trên Windows/Mac không có device_path rõ ràng, dùng index làm key tạm thời
            device_id_temp = f"Index_{i}" 
            
            cameras[device_id_temp] = {
                'name': f"Camera Index {i}",
                'os_index': i
            }
            cap.release()
        else:
            pass
            
    return cameras


def get_connected_cameras() -> Dict[str, Dict[str, Any]]:
    """Trả về dict: {device_id/device_path: {'name', 'os_index'}}"""
    current_os = platform.system()
    
    if current_os == 'Linux':
        return _get_linux_cameras()
    elif current_os == 'Windows' or current_os == 'Darwin':
        return _get_other_os_cameras()
    else:
        return {}


# ----------------------------------------------------------------------
# 3. Camera Management Service (Logic Nghiệp vụ và Upsert)
# ----------------------------------------------------------------------

class CameraManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.camera_crud = camera_crud 
        self.CameraDBModel = models.Camera 

    def upsert_camera_list(self) -> List[CameraResponse]:
        """
        Quét camera đang kết nối và đồng bộ với CSDL.
        - Cập nhật trạng thái 'ACTIVE' cho camera đang kết nối.
        - Cập nhật trạng thái 'DISCONNECTED' cho camera đã có trong DB nhưng bị rút.
        - Thêm mới camera lần đầu tiên được phát hiện.
        """
        connected_cameras = get_connected_cameras()
        db_cameras_list = self.camera_crud.get_all(self.db)
        
        connected_ids = set(connected_cameras.keys())
        updated_cameras: List[CameraResponse] = []
        
        # 2. Xử lý Camera đã có trong DB
        for db_camera in db_cameras_list:
            db_id = str(db_camera.device_id) 
            
            if db_id in connected_ids:
                # 2a. Camera đang kết nối (ACTIVE): Cập nhật thông tin
                new_info = connected_cameras[db_id]
                
                # Chuẩn bị data cho upsert (Dữ liệu này sẽ là Dict<str, Any>)
                camera_data = {
                    'name': new_info['name'],
                    'unique_id': db_id, # Đảm bảo NOT NULL khi tạo mới (upsert)
                    'device_id': db_id,
                    'status': 'ACTIVE',
                    'is_connected': 1, # SQLAlchemy Models dùng 1/0
                    'os_index': new_info['os_index'],
                    'device_path': db_id # Lưu trữ ID/Path của thiết bị
                }
                
                updated_db_camera = self.camera_crud.upsert(self.db, camera_data)
                
                # Chuyển đổi SQLAlchemy Model sang Pydantic Model Output (CameraResponse)
                # Lỗi cũ đã được sửa bằng cách sử dụng CameraResponse rõ ràng.
                updated_cameras.append(CameraResponse.from_orm(updated_db_camera))
                
                connected_ids.remove(db_id)
            else:
                # 2b. Camera bị rút (DISCONNECTED): Cập nhật trạng thái nếu đang ACTIVE
                if db_camera.status == "ACTIVE":
                    
                    camera_data = {
                        'device_id': db_id, 
                        'status': 'DISCONNECTED',
                        'is_connected': 0,
                    }
                    
                    updated_db_camera = self.camera_crud.upsert(self.db, camera_data)
                    updated_cameras.append(CameraResponse.from_orm(updated_db_camera))
                else:
                    # Giữ nguyên trạng thái (ví dụ: đã DISCONNECTED hoặc ERROR)
                    updated_cameras.append(CameraResponse.from_orm(db_camera))

        # 3. Xử lý Camera MỚI: Chỉ còn lại các ID mới trong connected_ids
        for new_id in connected_ids:
            new_info = connected_cameras[new_id]
            
            # Chuẩn bị data cho upsert (Tạo mới)
            new_camera_data = {
                'name': new_info['name'],
                'unique_id': new_id, # Bắt buộc phải có để tạo mới
                'device_id': new_id, 
                'status': 'ACTIVE',
                'is_connected': 1,
                'os_index': new_info['os_index'],
                'device_path': new_id
            }
            
            # Sử dụng upsert (sẽ tạo mới vì không tìm thấy device_id)
            new_db_camera = self.camera_crud.upsert(self.db, new_camera_data)
            updated_cameras.append(CameraResponse.from_orm(new_db_camera))
            
        return updated_cameras


# ----------------------------------------------------------------------
# 4. Hướng dẫn Tách Luồng
# ----------------------------------------------------------------------

def run_camera_upsert_loop(db_session_factory: Any, interval_seconds: int = 5):
    """
    Hàm này chạy trong luồng riêng biệt để định kỳ cập nhật danh sách camera.
    db_session_factory phải là một generator/callable trả về Session.
    """
    print(f"Camera Management Service started (interval: {interval_seconds}s)")
    while True:
        db = None
        try:
            # Lấy Session mới cho mỗi chu kỳ
            db: Session = next(db_session_factory())
            service = CameraManagementService(db)
            
            updated_list = service.upsert_camera_list()
            active_count = len([c for c in updated_list if c.status == 'ACTIVE'])
            print(f"[{time.strftime('%H:%M:%S')}] Camera list updated. Total: {len(updated_list)}, Active: {active_count}")

            
        except Exception as e:
            # Lỗi Pydantic, DB, hoặc Logic
            error_msg = str(e)
            if 'AttributeError' in error_msg and "'dict' object has no attribute 'dict'" in error_msg:
                 # In rõ ràng lỗi này để dễ debug
                 print("Cảnh báo: Lỗi Pydantic/ORM mapping. Đảm bảo CameraResponse.from_orm() được gọi đúng.")
            
            print(f"ERROR in Camera Management Loop: {e}")
        
        finally:
            # Đảm bảo Session luôn được đóng
            if db:
                db.close()
                
        time.sleep(interval_seconds)