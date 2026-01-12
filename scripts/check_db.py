# scripts/check_db.py
import sys
import os
import sqlite3
from passlib.hash import argon2

# --- THÊM ĐOẠN NÀY ĐỂ IMPORT ĐƯỢC CONFIG TỪ APP ---
# Thêm thư mục gốc vào path để import được 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from app.core.config import settings
# --------------------------------------------------

# Tự động lấy đường dẫn file DB từ cấu hình
# settings.DB_URL ví dụ: "sqlite:///./app/db/adocv1.db"
if "sqlite" in settings.DB_URL:
    # Cắt bỏ phần prefix "sqlite:///" để lấy đường dẫn file thực tế
    DB_FILE = settings.DB_URL.replace("sqlite:///", "")
    # Xử lý nếu đường dẫn là tương đối (bắt đầu bằng .)
    if DB_FILE.startswith("."):
        DB_FILE = os.path.join(root_dir, DB_FILE)
else:
    print(f"❌ Script này chỉ hỗ trợ SQLite. DB hiện tại là: {settings.DB_URL}")
    sys.exit(1)

INIT_SQL = os.path.join(root_dir, "app/db/migrations/init.sql")

def init_db_tables():
    print(f"⏳ Đang làm việc với Database: {DB_FILE}")
    
    # Tạo thư mục chứa db nếu chưa có
    db_dir = os.path.dirname(DB_FILE)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(DB_FILE)
    try:
        if not os.path.exists(INIT_SQL):
            print(f"❌ Không tìm thấy file SQL tại: {INIT_SQL}")
            return

        with open(INIT_SQL, "r", encoding="utf-8") as f:
            init_sql = f.read()
        conn.executescript(init_sql)
        conn.commit()
        print("✅ Cấu trúc bảng đã được cập nhật.")
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo bảng: {e}")
    finally:
        conn.close()

def ensure_admin_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        if count == 0:
            print("⚡ Bảng users rỗng, tạo user admin mặc định...")
            password_hash = argon2.hash("123456") 
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role, is_active) VALUES (?, ?, ?, ?, ?)",
                ("admin", password_hash, "Administrator", "admin", 1)
            )
            conn.commit()
            print("✅ User 'admin' đã được tạo.")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Lỗi truy vấn (có thể bảng chưa tạo): {e}")
    finally:
        conn.close()

def main():
    init_db_tables()
    ensure_admin_user()

if __name__ == "__main__":
    main()