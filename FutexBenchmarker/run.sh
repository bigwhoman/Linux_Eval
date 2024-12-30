#!/bin/bash
gcc -o futex_benchmark futex_bench.c -pthread

./futex_benchmark 1000000 > futex_benchmark-$(uname -r).txt
