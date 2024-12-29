#!/bin/bash
sudo apt update
sudo apt install mysql-server
sudo apt install sysbench
sudo systemctl start mysql
echo "Enter your password to generate database"
mysql -u root -p -e "CREATE DATABASE sysbench_test22;"
mysql -u root -p -e "CREATE USER 'sysbench_user22'@'localhost' IDENTIFIED BY 'password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON sysbench_test22.* TO 'sysbench_user22'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"


