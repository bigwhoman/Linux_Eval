#!/bin/bash
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root or with sudo privileges"
   exit 1
fi

sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password --table-size=1000000 --threads=4 prepare
strace -f -p "$(pidof mysqld)" 2> "mysql-$(uname -r).strace"&
STRACE_PID=$!
sleep 5
sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password --table-size=1000000 --threads=4 --time=120 run > $(uname -r)-log.txt
sleep 5
kill -s SIGINT "$STRACE_PID"
sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password cleanup


