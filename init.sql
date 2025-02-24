CREATE DATABASE IF NOT EXISTS `${MYSQLDATABASE}`;

CREATE USER IF NOT EXISTS '${MYSQLUSER}'@'%' IDENTIFIED WITH 'caching_sha2_password' BY '${MYSQLPASSWORD}';

GRANT ALL PRIVILEGES ON `${MYSQLDATABASE}`.* TO '${MYSQLUSER}'@'%';

FLUSH PRIVILEGES;
