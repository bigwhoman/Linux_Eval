#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# # Check for FlameGraph tools
# if [ ! -d "FlameGraph" ]; then
#     echo "Downloading FlameGraph tools..."
#     git clone https://github.com/brendangregg/FlameGraph.git
# fi

# Create test directory and files
WORK_DIR=$(uname -r)"-X-test"
mkdir -p $WORK_DIR
cp munmap_test.c $WORK_DIR
cd $WORK_DIR

# # Create test file
# echo "test data" > test.txt

# Create the test program
# cat > test.c << 'EOF'
# #include <unistd.h>
# #include <fcntl.h>
# #include <stdio.h>

# int main() {
#     char buf[10];
#     int fd = open("test.txt", O_RDONLY);
#     if (fd < 0) {
#         perror("open failed");
#         return 1;
#     }
#     read(fd, buf, 1);
#     close(fd);
#     return 0;
# }
# EOF

# Compile
gcc -g munmap_test.c -o test

# Setup tracing
# First, disable kernel pointer restriction
sudo sh -c "echo 0 > /proc/sys/kernel/kptr_restrict"

# Clear existing trace and set up new trace
trace-cmd reset

# Record the trace with function_graph tracer
# -p function_graph : sets the tracer
# -g sys_read : sets the graph function to trace
# -O funcgraph-proc : enables process information in the graph
trace-cmd record -p function_graph -g __do_munmap -g do_mmap -O funcgraph-proc ./test

# The trace will be automatically saved to trace.dat
# To save it to your desired location:
mkdir -p trace_output
mv trace.dat trace_output/

# To view the trace in readable format:
trace-cmd report trace_output/trace.dat > trace_output/ftrace_output.txt

# # Process ftrace output for flamegraph
# echo "Converting ftrace output to flamegraph format..."
# cat trace_output/ftrace_output.txt | awk '
# BEGIN { stackcount = 0; }
# /^  [0-9]/ {
#     line = $0;
#     sub(/^[ ]*[0-9]+\)|[ ]+/, "", line);
#     sub(/\{$/, "", line);
#     if (line ~ /^[a-zA-Z]/) {
#         depth = int(length($0) - length(line));
#         stack[depth] = line;
#         stackcount++;
#         if (stackcount % 100 == 0) {  # Print every 100th stack
#             for (i = 0; i <= depth; i++) {
#                 printf "%s", stack[i];
#                 if (i < depth) printf ";";
#             }
#             printf " 1\n";
#         }
#     }
# }' > trace_output/ftrace.folded

# # Generate flamegraph
# echo "Generating flamegraph..."
# ../FlameGraph/flamegraph.pl trace_output/ftrace.folded > trace_output/ftrace_flame.svg

# echo "Done! Generated files:"
# echo "- Raw ftrace output: trace_output/ftrace_output.txt"
# echo "- Folded stacks: trace_output/ftrace.folded"
# echo "- Flamegraph: trace_output/ftrace_flame.svg"

# # Show the folded stack content
# echo -e "\nFirst few lines of the folded stack:"
# head -n 5 trace_output/ftrace.folded

# # Optional cleanup
# echo -e "\nDo you want to clean up the test files? (y/n)"
# read -r answer
# if [[ "$answer" =~ ^[Yy]$ ]]; then
#     cd ..
#     rm -rf $WORK_DIR
#     echo "Cleanup complete."
# fi
