-- Insert sample orders
INSERT INTO orders (camera_id, user_id, session_id, code, status, start_at, note)
VALUES
(1, 1, 'sess-001', 'ORD001', 'packing', CURRENT_TIMESTAMP, 'First test order'),
(2, 2, 'sess-002', 'ORD002', 'closed', CURRENT_TIMESTAMP, 'Closed order sample'),
(1, 3, 'sess-003', 'ORD003', 'error', CURRENT_TIMESTAMP, 'Error order sample');