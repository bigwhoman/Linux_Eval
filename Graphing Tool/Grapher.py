import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import re
from packaging import version

def extract_version(filename):
    """
    Extract Linux version number from filename, keeping only major.minor (e.g., 5.15)
    Example: 'output.5.15.104_2.csv' -> '5.15'
    """
    match = re.search(r'output\.(\d+\.\d+)', filename)
    if match:
        version_str = match.group(1)
        return version_str
    return filename

def version_key(ver_str):
    """
    Convert version string to a comparable version object
    """
    return version.parse(ver_str)

def read_benchmark_csv(file_path):
    """
    Read and process a benchmark CSV file.
    Returns a dictionary of test names and their 'kbest' values.
    """
    # Read CSV, skip the first row which contains the header "OS Benchmark experiment"
    try:
        df = pd.read_csv(file_path, skiprows=1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}
    
    # Initialize dictionary to store results
    results = {}
    
    # Process each row
    for _, row in df.iterrows():
        # Get test name and type (kbest/average)
        test_info = str(row.iloc[0]).strip()
        if not isinstance(test_info, str) or pd.isna(test_info):
            continue
            
        # Split into test name and type
        parts = test_info.rsplit(None, 1)
        if len(parts) != 2 or parts[1] not in ['kbest:', 'average:']:
            continue
            
        test_name, metric_type = parts
        test_name = test_name.strip()
        
        # Store only 'kbest' values
        if metric_type == 'kbest:':
            try:
                # Convert to float and validate
                value = float(row.iloc[1])
                if pd.isna(value) or np.isinf(value):
                    print(f"Warning: Invalid value for {test_name}: {value}")
                    continue
                results[test_name] = value
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert value for {test_name}: {row.iloc[1]}")
                continue
    
    return results

def combine_version_data(data):
    """
    Combine multiple measurements for the same major.minor version by taking the minimum value
    """
    combined_data = {}
    for version, measurements in data.items():
        if version not in combined_data:
            combined_data[version] = measurements
        else:
            # For each test, take the minimum value (best performance)
            for test, value in measurements.items():
                if test in combined_data[version]:
                    combined_data[version][test] = min(combined_data[version][test], value)
                else:
                    combined_data[version][test] = value
    return combined_data

def create_heatmap(csv_folder, center_version):
    """
    Create a heatmap showing relative performance differences.
    """
    # Get all CSV files
    csv_folder = Path(csv_folder)
    csv_files = sorted(csv_folder.glob('*.csv'))
    
    if not csv_files:
        raise ValueError(f"No CSV files found in {csv_folder}")
    
    # Read all data
    data = {}
    for file in csv_files:
        version = extract_version(file.name)
        file_data = read_benchmark_csv(file)
        if file_data:  # Only add if we got valid data
            data[version] = file_data
    
    if not data:
        raise ValueError("No valid data could be read from CSV files")
    
    # Combine data for same major.minor versions
    data = combine_version_data(data)
    
    # Verify center version exists
    if center_version not in data:
        raise ValueError(f"Center version {center_version} not found in data. Available versions: {list(data.keys())}")
    
    # Get all unique tests
    all_tests = sorted(set().union(*[set(d.keys()) for d in data.values()]))
    
    # Sort versions properly using version_key function
    versions = sorted(data.keys(), key=version_key)
    
    # Create DataFrame for relative differences
    df_relative = pd.DataFrame(index=all_tests, columns=versions, dtype=float)
    
    # Calculate relative differences
    center_data = data[center_version]
    for test in all_tests:
        if test in center_data and center_data[test] != 0:  # Avoid division by zero
            center_value = center_data[test]
            for version in versions:
                if test in data[version]:
                    # Calculate percentage difference
                    relative_diff = ((data[version][test] - center_value) / center_value) * 100
                    df_relative.at[test, version] = relative_diff
    
    # Fill NaN values with 0 for better visualization
    df_relative = df_relative.fillna(0)
    
    # Create heatmap
    plt.figure(figsize=(20, 12))
    sns.heatmap(df_relative, 
                cmap='RdYlBu_r',
                center=0,
                vmin=-50,
                vmax=150,
                annot=True,
                fmt='.0f',
                cbar_kws={'label': 'Percentage Change'})
    
    plt.title(f'Percentage Change in Test Latency Relative to {center_version}')
    plt.xlabel('Linux Version')
    plt.ylabel('Test Name')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('performance_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Example usage
    csv_folder = "."  # Current directory, or specify your folder path
    center_version = "5.14"  # The version to use as reference (only major.minor)
    
    try:
        create_heatmap(csv_folder, center_version)
        print("Heatmap created successfully as 'performance_heatmap.png'")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nDebug information:")
        print("Please check:")
        print("1. CSV files are in the correct format")
        print("2. All data values are numeric")
        print("3. The center version exists in your dataset")
