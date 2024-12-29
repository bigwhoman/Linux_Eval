#!/bin/bash

# Check for Python installation
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3 to proceed."
    exit 1
fi

# Check for strace installation
if ! command -v strace &> /dev/null
then
    echo "strace is not installed. Please install strace to proceed."
    exit 1
fi

# Create a timestamp for unique filenames
timestamp=$(date +%Y%m%d_%H%M%S)
kernel_version=$(uname -r)

# Run the Python benchmark script with strace
echo "Starting PyTorch Benchmark with syscall tracking..."

# Use strace with the following flags:
# -f: trace child processes
# -tt: add time stamps with microsecond precision
# -o: output to file
# strace -f -tt -o "strace_log-${kernel_version}-${timestamp}.txt" \
    python3 benchmark.py > "benchmark_log-${kernel_version}-${timestamp}.txt" 2>&1

# Output completion message
echo "PyTorch Benchmark Completed!"
echo "Benchmark output saved to: benchmark_log-${kernel_version}-${timestamp}.txt"
echo "Syscall trace saved to: strace_log-${kernel_version}-${timestamp}.txt"