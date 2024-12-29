#!/bin/bash

# Check for Python installation
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed. Please install Python3 to proceed."
    exit 1
fi

# Run the Python benchmark script
echo "Starting PyTorch Benchmark..."
python3 benchmark.py > benchmark_log.txt

# Output completion message
echo "PyTorch Benchmark Completed!"
