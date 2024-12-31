import re
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import numpy as np
import sys

def parse_strace_file(file_path):
    # Updated pattern to match pid and syscall names even with resumed calls
    syscall_pattern = r'\[pid\s+\d+\]\s+(?:<\.\.\.\s+)?(\w+)(?:\s+resumed>|\()'
    
    syscalls = []
    with open(file_path, 'r') as file:
        content = file.read()
        matches = re.finditer(syscall_pattern, content)
        for match in matches:
            syscall_name = match.group(1)
            # Skip if it's not actually a syscall
            if syscall_name not in ['resumed']:
                syscalls.append(syscall_name)
    
    return syscalls

def analyze_syscalls(syscalls, min_percentage=1.0):
    if not syscalls:
        print("No syscalls were found in the input file!")
        return pd.DataFrame(), pd.DataFrame()
    
    # Count syscalls
    syscall_counts = Counter(syscalls)
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame.from_dict(syscall_counts, orient='index', columns=['count'])
    df.index.name = 'syscall'
    df = df.reset_index()
    
    # Calculate percentages
    total_calls = df['count'].sum()
    df['percentage'] = (df['count'] / total_calls * 100).round(2)
    
    # Sort by count in descending order
    df = df.sort_values('count', ascending=False)
    
    # Filter out syscalls below threshold
    df_filtered = df[df['percentage'] >= min_percentage].copy()
    
    # Add an "Others" category for the filtered syscalls
    if len(df_filtered) < len(df):
        others_count = df[df['percentage'] < min_percentage]['count'].sum()
        others_percentage = df[df['percentage'] < min_percentage]['percentage'].sum()
        others_row = pd.DataFrame({
            'syscall': ['Others'],
            'count': [others_count],
            'percentage': [others_percentage.round(2)]
        })
        df_filtered = pd.concat([df_filtered, others_row], ignore_index=True)
    
    return df_filtered, df

def create_visualizations(df_filtered, df_full, output_file=f'syscall_analysis_{sys.argv[1]}.png'):
    if df_filtered.empty or df_full.empty:
        print("No data to visualize!")
        return
        
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Color map with a distinct color for "Others"
    colors = plt.cm.Set3(np.linspace(0, 1, len(df_filtered)))
    if 'Others' in df_filtered['syscall'].values:
        colors[-1] = [0.7, 0.7, 0.7, 1.0]  # Gray color for "Others"
    
    # Bar chart
    bars = ax1.bar(df_filtered['syscall'], df_filtered['count'], color=colors)
    ax1.set_title('System Call Distribution (>= 1% of total)', fontsize=14, pad=20)
    ax1.set_xlabel('System Call', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.tick_params(axis='x', rotation=45, labelsize=10)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom')
    
    # Pie chart
    wedges, texts, autotexts = ax2.pie(
        df_filtered['count'], 
        labels=df_filtered['syscall'], 
        autopct='%1.1f%%',
        colors=colors
    )
    ax2.set_title('System Call Percentage Distribution', fontsize=14, pad=20)
    
    # Make the percentage labels easier to read
    plt.setp(autotexts, size=9, weight="bold")
    plt.setp(texts, size=10)
    
    # Add a legend to the pie chart
    ax2.legend(wedges, df_filtered['syscall'],
              title="System Calls",
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))
    
    # Adjust layout to prevent overlapping
    plt.tight_layout()
    
    # Save the plots
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()

def print_statistics(df_filtered, df_full, total_syscalls):
    print("\nSystem Call Analysis Summary")
    print("=" * 50)
    print(f"Total number of system calls: {total_syscalls:,}")
    print(f"Number of unique system calls: {len(df_full):,}")
    
    print("\nTop System Calls (>= 1% of total):")
    print("=" * 50)
    formatted_data = df_filtered.copy()
    formatted_data['count'] = formatted_data['count'].apply(lambda x: f"{int(x):,}")
    print(formatted_data.to_string(index=False))
    
    print("\nComplete System Call Distribution:")
    print("=" * 50)
    formatted_full = df_full.copy()
    formatted_full['count'] = formatted_full['count'].apply(lambda x: f"{int(x):,}")
    print(formatted_full.to_string(index=False))

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 syscall_analyzer.py <strace file>")
        sys.exit(1)

    file_path = sys.argv[1]
    min_percentage = 1.0  # Minimum percentage threshold
    
    # Parse and analyze syscalls
    print(f"Analyzing {file_path}...")
    syscalls = parse_strace_file(file_path)
    
    if not syscalls:
        print("Error: No syscalls found in the input file!")
        return
        
    total_syscalls = len(syscalls)
    df_filtered, df_full = analyze_syscalls(syscalls, min_percentage)
    
    # Create visualizations
    create_visualizations(df_filtered, df_full)
    
    # Print statistics
    print_statistics(df_filtered, df_full, total_syscalls)
    
    print(f"\nVisualizations have been saved as 'syscall_analysis.png'")

if __name__ == "__main__":
    main()