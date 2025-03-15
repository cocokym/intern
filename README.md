## Prerequisites Installation
1. Install Python 3.9 or later:
 Download from https://www.python.org/downloads/
 Make sure to check "Add Python to PATH" during installation
2. Install MySQL:
 Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
 Note the root password during installation
## Project Setup
 1. clone the repository
 git clone https://github.com/cocokym/intern.git
 2. Install required packages:
 pip install -r requirements.txt
## Database Setup
 1. Start MySQL and create the database:
 mysql -u root -p

 CREATE DATABASE patients_db;

 CREATE USER 'remote_user'@'localhost' IDENTIFIED BY 'password';

 GRANT ALL PRIVILEGES ON patients_db.* TO 'remote_user'@'localhost';

 FLUSH PRIVILEGES;

 EXIT;
 
2. Import the database backup:
 mysql -u remote_user -p patients_db < patients_db_backup.sql
## Testing the Setup
1. Test database connection:
 python3 test_db.py

