-- Password hashes are for demo only; replace with BCrypt output from the app.
INSERT OR IGNORE INTO users (name, email, password_hash, role)
VALUES
('Admin User', 'admin@churnsight.local', 'REPLACE_WITH_BCRYPT', 'admin'),
('Analyst User', 'analyst@churnsight.local', 'REPLACE_WITH_BCRYPT', 'analyst'),
('Viewer User', 'viewer@churnsight.local', 'REPLACE_WITH_BCRYPT', 'viewer');