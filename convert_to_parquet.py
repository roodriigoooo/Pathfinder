"""
Script to convert CSV files to Parquet format for the Pathfinder application.
This will reduce the disk space used by the data files.
"""

import pandas as pd
import os
import glob

def convert_csv_to_parquet(csv_path, parquet_path=None):
    if parquet_path is None:
        parquet_path = csv_path.replace('.csv', '.parquet')
    
    try:
        # Read the CSV file
        print(f"Reading {csv_path}...")
        df = pd.read_csv(csv_path, low_memory=False)
        
        # Convert to Parquet
        print(f"Converting to Parquet: {parquet_path}")
        df.to_parquet(parquet_path, index=False)
        
        # Get file sizes for comparison
        csv_size = os.path.getsize(csv_path) / (1024 * 1024)  # Size in MB
        parquet_size = os.path.getsize(parquet_path) / (1024 * 1024)  # Size in MB
        reduction = (1 - parquet_size / csv_size) * 100  # Percentage reduction
        
        return True, f"Converted {csv_path} to {parquet_path}. Size reduced from {csv_size:.2f}MB to {parquet_size:.2f}MB ({reduction:.2f}% reduction)"
    
    except Exception as e:
        return False, f"Error converting {csv_path}: {str(e)}"

def main():
    """
    Convert all CSV files used in the Pathfinder application to Parquet format.
    """
    # Define the files to convert
    files_to_convert = [
        "data/Most-Recent-Cohorts-Institution.csv",
        "data/FieldOfStudyData1819_1920_PP.csv"
    ]
    
    # Add historical data files
    historical_files = glob.glob("data/MERGED*.csv")
    files_to_convert.extend(historical_files)
    
    # Convert each file
    total_files = len(files_to_convert)
    success_count = 0
    
    print(f"Found {total_files} CSV files to convert.")
    
    for file_path in files_to_convert:
        if os.path.exists(file_path):
            success, message = convert_csv_to_parquet(file_path)
            print(message)
            if success:
                success_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nConversion complete: {success_count}/{total_files} files converted successfully.")

if __name__ == "__main__":
    main()
