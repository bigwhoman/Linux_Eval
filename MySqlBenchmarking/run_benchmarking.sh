#!/bin/bash


sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password --table-size=1000000 --threads=4 prepare

sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password --table-size=1000000 --threads=4 --time=120 run

sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password cleanup



