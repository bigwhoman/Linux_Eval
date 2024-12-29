#!/usr/bin/env python3

import sys
import subprocess
import re
from collections import defaultdict

# Configuration
MIN_DURATION_US = 0.1    # Minimum duration in microseconds to include a function
MAX_STACK_DEPTH = 5      # Maximum depth of the call stack to track
TARGET_FUNCTION = "do_mas_munmap"  # The root function we want to analyze

def parse_duration(duration_str):
    """Parse duration string and convert to microseconds"""
    try:
        if duration_str.startswith('+'):
            duration_str = duration_str[1:].strip()
        if duration_str.startswith('!'):
            duration_str = duration_str[1:].strip()
        return float(duration_str)
    except ValueError:
        return 0.0

def parse_tracecmd(input_file):
    try:
        cmd = ['trace-cmd', 'report', input_file]
        output = subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running trace-cmd: {e}", file=sys.stderr)
        sys.exit(1)

    # Process the output
    stacks = defaultdict(float)  # Using float for duration accumulation
    current_stack = []
    in_target_function = False
    found_first = False
    
    # Regular expressions for matching function entry/exit
    entry_pattern = re.compile(r'funcgraph_entry:\s*(?:(\d+\.\d+)\s+us\s+)?\|\s*(\w+)\(\)\s*{')
    exit_pattern = re.compile(r'funcgraph_exit:\s*(?:[\+\!])?\s*(\d+\.\d+)\s+us\s*\|\s*}')
    single_line_pattern = re.compile(r'funcgraph_entry:\s*(\d+\.\d+)\s+us\s*\|\s*(\w+)\(\);')
    
    for line in output.split('\n'):
        line = line.strip()
        
        # Skip empty lines and CPU info
        if not line or line.startswith('CPU') or line.startswith('cpus='):
            continue

        # If we've already processed the first instance and we're not in a stack, stop
        if found_first and not current_stack:
            break

        # Check for single-line function calls first
        single_line_match = single_line_pattern.search(line)
        if single_line_match:
            duration = parse_duration(single_line_match.group(1))
            func_name = single_line_match.group(2)
            
            if in_target_function and duration >= MIN_DURATION_US:
                # For single-line functions, create a temporary stack including this function
                temp_stack = current_stack + [func_name]
                if len(temp_stack) <= MAX_STACK_DEPTH:
                    stack_str = ';'.join(temp_stack)
                    stacks[stack_str] = duration
            
            # If this is our target function (unlikely as it's single-line, but possible)
            if func_name == TARGET_FUNCTION:
                found_first = True
                in_target_function = False
            continue

        # Check for function entry
        entry_match = entry_pattern.search(line)
        if entry_match:
            func_name = entry_match.group(2)
            
            # Check for target function
            if func_name == TARGET_FUNCTION and not in_target_function:
                in_target_function = True
                current_stack = []
            
            # Only add to stack if we're tracking and haven't reached max depth
            if in_target_function and len(current_stack) < MAX_STACK_DEPTH:
                current_stack.append(func_name)
            continue

        # Check for function exit
        exit_match = exit_pattern.search(line)
        if exit_match and current_stack:
            duration = parse_duration(exit_match.group(1))
            
            if in_target_function and duration >= MIN_DURATION_US:
                stack_str = ';'.join(current_stack)
                stacks[stack_str] = duration
            
            func_name = current_stack.pop() if current_stack else None
            
            # Stop after completing the first target function
            if func_name == TARGET_FUNCTION:
                found_first = True
                in_target_function = False

    return stacks

def write_folded_format(stacks, output_file):
    """Write stacks in folded format required by flamegraph.pl"""
    with open(output_file, 'w') as f:
        for stack, duration in sorted(stacks.items()):
            # Convert duration to sample count (1 sample per microsecond)
            samples = float(duration)
            if samples > 0:
                f.write(f"{stack} {samples}\n")

def main():
    input_file = "trace.dat"
    output_file = "output.folded"

    print(f"Processing {input_file}...")
    print(f"Analyzing first occurrence of: {TARGET_FUNCTION}")
    print(f"Settings:")
    print(f"- Minimum duration: {MIN_DURATION_US}μs")
    print(f"- Maximum stack depth: {MAX_STACK_DEPTH}")

    stacks = parse_tracecmd(input_file)
    
    # Print the actual stacks before writing to file
    print("\nStack traces to be graphed:")
    for stack, duration in sorted(stacks.items()):
        print(f"{stack}: {duration:.2f}μs")
    
    write_folded_format(stacks, output_file)
    
    # Calculate stats
    max_depth = max((stack.count(';') + 1 for stack in stacks.keys()), default=0)
    total_time = max((duration for duration in stacks.values()), default=0)
    
    print(f"\nFirst instance statistics:")
    print(f"- Total time: {total_time:.2f}μs")
    print(f"- Maximum stack depth: {max_depth}")
    print(f"- Number of unique stacks: {len(stacks)}")
    
    print(f"\nOutput written to {output_file}")
    print("\nNow you can generate the flame graph using:")
    print(f"flamegraph.pl --width 800 --height 400 --minwidth 0.5 "
          f"--title 'First {TARGET_FUNCTION} ({total_time:.0f}μs)' "
          f"--countname 'microseconds' {output_file} > flamegraph.svg")

if __name__ == '__main__':
    main()