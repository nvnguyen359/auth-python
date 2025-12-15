# scripts/check_db.py
import os, sqlite3
from passlib.hash import argon2

DB_FILE = "./app/db/adocv1.db"
INIT_SQL = "./app/db/migrations/init.sql"
SAMPLE_SQL = "./app/db/migrations/sample.sql"

def ensure_admin_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
    conn.close()

def main():
    if not os.path.exists(DB_FILE):
        print("➡ Tạo mới DB...")
        with open(INIT_SQL, "r", encoding="utf-8") as f:
            init_sql = f.read()
        conn = sqlite3.connect(DB_FILE)
        conn.executescript(init_sql)
        conn.commit()
        conn.close()
        print("✅ Database đã tạo.")
    ensure_admin_user()

if __name__ == "__main__":
    main()
