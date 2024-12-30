import re
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import numpy as np

def parse_strace_file(file_path):
    # Regular expression to match syscall names
    syscall_pattern = r'\d+\s+[\d:.]+\s+(\w+)\('
    
    syscalls = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(syscall_pattern, line)
            if match:
                syscall_name = match.group(1)
                syscalls.append(syscall_name)
    
    return syscalls

def analyze_syscalls(syscalls, min_percentage=1.0):
    # Count syscalls
    syscall_counts = Counter(syscalls)
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame.from_dict(syscall_counts, orient='index', columns=['count'])
    df.index.name = 'syscall'
    df = df.reset_index()
    
    # Calculate percentages
    total_calls = df['count'].sum()
    df['percentage'] = (df['count'] / total_calls * 100).round(2)
    
    # Filter out syscalls below threshold
    df_filtered = df[df['percentage'] >= min_percentage]
    
    # Add an "Others" category for the filtered syscalls
    if len(df_filtered) < len(df):
        others_count = df[df['percentage'] < min_percentage]['count'].sum()
        others_percentage = df[df['percentage'] < min_percentage]['percentage'].sum()
        others_row = pd.DataFrame({
            'syscall': ['Others'],
            'count': [others_count],
            'percentage': [others_percentage]
        })
        df_filtered = pd.concat([df_filtered, others_row], ignore_index=True)
    
    # Sort by count in descending order
    df_filtered = df_filtered.sort_values('count', ascending=False)
    
    return df_filtered, df

def create_visualizations(df_filtered, df_full):
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Color map with a distinct color for "Others"
    colors = plt.cm.Set3(np.linspace(0, 1, len(df_filtered)))
    if 'Others' in df_filtered['syscall'].values:
        colors[-1] = [0.7, 0.7, 0.7, 1.0]  # Gray color for "Others"
    
    # Bar chart
    ax1.bar(df_filtered['syscall'], df_filtered['count'], color=colors)
    ax1.set_title('Syscall Counts (>= 1% of total)')
    ax1.set_xlabel('Syscall')
    ax1.set_ylabel('Count')
    ax1.tick_params(axis='x', rotation=45)
    
    # Pie chart
    wedges, texts, autotexts = ax2.pie(
        df_filtered['count'], 
        labels=df_filtered['syscall'], 
        autopct='%1.1f%%',
        textprops={'fontsize': 7},
        colors=colors
    )
    ax2.set_title('Syscall Distribution (%)')
    
    # Adjust layout to prevent overlapping
    plt.tight_layout()
    
    # Save the plots
    plt.savefig('syscall_analysis.png', bbox_inches='tight', dpi=300)
    
    # Print tabular data
    print("\nFiltered Syscall Analysis (>= 1% of total):")
    print("=" * 50)
    print(df_filtered.to_string(index=False))
    
    print("\nFull Syscall Analysis:")
    print("=" * 50)
    print(df_full.to_string(index=False))

def main():
    import numpy as np  # Added import for np.linspace
    
    file_path = 'strace_log-5.19.0-32-generic-.txt'  # Replace with your file path
    min_percentage = 1.0  # Minimum percentage threshold
    
    # Parse and analyze syscalls
    syscalls = parse_strace_file(file_path)
    df_filtered, df_full = analyze_syscalls(syscalls, min_percentage)
    
    # Create and save visualizations
    create_visualizations(df_filtered, df_full)
    print(f"\nVisualizations have been saved as 'syscall_analysis.png'")
    print(f"Note: Syscalls appearing less than {min_percentage}% of the time are grouped as 'Others'")

if __name__ == "__main__":
    main()
