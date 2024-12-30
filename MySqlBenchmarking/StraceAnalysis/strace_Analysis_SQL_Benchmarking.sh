#!/bin/bash

# Check for strace installation
if ! command -v strace &> /dev/null
then
    echo "strace is not installed. Please install strace to proceed."
    exit 1
fi

kernel_version=$(uname -r)

sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password --table-size=1000000 --threads=4 prepare


# Use strace with the following flags:
# -f: trace child processes
# -tt: add time stamps with microsecond precision
# -o: output to file
strace -f -tt -o "strace_log-${kernel_version}-${timestamp}.txt" \
sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password --table-size=1000000 --threads=4 --time=120 run > "benchmark_log-${kernel_version}.txt" 2>&1



sysbench oltp_read_write --db-driver=mysql --mysql-db=sysbench_test --mysql-user=sysbench_user --mysql-password=password cleanup


