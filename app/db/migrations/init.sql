-- db/migrations/init.sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'operator',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    status TEXT,
    unique_id TEXT UNIQUE NOT NULL,
    device_id TEXT UNIQUE NOT NULL,
    display_name TEXT,
    rtsp_url TEXT,
    backend TEXT,
    prefer_gst INTEGER DEFAULT 0,
    is_connected INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_path TEXT,  -- Đã thêm dấu phẩy ở đây
    os_index INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id INTEGER,
    user_id INTEGER,
    parent_id INTEGER,
    session_id TEXT,
    code TEXT,
    status TEXT DEFAULT 'packing',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_at DATETIME,
    closed_at DATETIME,
    path_avatar TEXT,
    path_video TEXT,
    order_metadata TEXT,
    note TEXT,
    -- Khóa ngoại
    FOREIGN KEY(camera_id) REFERENCES cameras(id) ON DELETE SET NULL,
    FOREIGN KEY(parent_id) REFERENCES orders(id) ON DELETE SET NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(255) NOT NULL UNIQUE,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);