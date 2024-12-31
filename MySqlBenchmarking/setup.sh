#!/bin/bash
sudo apt update
sudo apt install mysql-server
sudo apt install sysbench
sudo systemctl start mysql
echo "Enter your password to generate database"
mysql -u root -p -e "CREATE DATABASE sysbench_test;"
mysql -u root -p -e "CREATE USER 'sysbench_user'@'localhost' IDENTIFIED BY 'password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON sysbench_test.* TO 'sysbench_user'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"


