CREATE USER IF NOT EXISTS 'checker'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'password';
GRANT ALL PRIVILEGES ON attendance.* TO 'checker'@'%';
FLUSH PRIVILEGES;
