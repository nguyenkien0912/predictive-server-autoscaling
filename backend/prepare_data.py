"""
Script to prepare data from NASA logs for the backend service
Run this before starting the backend to ensure data is available
"""

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

def parse_log_line(line):
    """Parse a single NASA log line"""
    pattern = r'(\S+) - - \[(.*?)\] "(.*?)" (\d+) (\S+)'
    match = re.match(pattern, line)
    
    if match:
        host = match.group(1)
        timestamp_str = match.group(2)
        request = match.group(3)
        status = int(match.group(4))
        bytes_str = match.group(5)
        
        # Parse timestamp
        try:
            timestamp = pd.to_datetime(timestamp_str, format='%d/%b/%Y:%H:%M:%S %z')
        except:
            return None
        
        # Parse bytes
        try:
            bytes_val = int(bytes_str) if bytes_str != '-' else 0
        except:
            bytes_val = 0
        
        return {
            'timestamp': timestamp,
            'host': host,
            'request': request,
            'status': status,
            'bytes': bytes_val
        }
    return None

def load_nasa_logs(file_path):
    """Load and parse NASA log file"""
    print(f"Loading {file_path}...")
    
    data = []
    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
        for i, line in enumerate(f):
            if i % 10000 == 0:
                print(f"  Processed {i} lines...")
            
            parsed = parse_log_line(line.strip())
            if parsed:
                data.append(parsed)
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    
    print(f"  Loaded {len(df)} records")
    return df

def main():
    """Main data preparation pipeline"""
    print("=" * 60)
    print("NASA Logs Data Preparation")
    print("=" * 60)
    
    # Define paths
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    jul_file = os.path.join(data_dir, 'access_log_Jul95.txt')
    aug_file = os.path.join(data_dir, 'access_log_Aug95.txt')
    output_file = os.path.join(data_dir, 'nasa_logs_processed.parquet')
    
    # Check if files exist
    if not os.path.exists(jul_file):
        print(f"WARNING: {jul_file} not found!")
        print("Creating dummy data for testing...")
        create_dummy_data(output_file)
        return
    
    if not os.path.exists(aug_file):
        print(f"WARNING: {aug_file} not found!")
        print("Creating dummy data for testing...")
        create_dummy_data(output_file)
        return
    
    # Load data
    print("\n1. Loading July logs...")
    df_jul = load_nasa_logs(jul_file)
    
    print("\n2. Loading August logs...")
    df_aug = load_nasa_logs(aug_file)
    
    # Combine
    print("\n3. Combining datasets...")
    df = pd.concat([df_jul, df_aug])
    df.sort_index(inplace=True)
    
    print(f"   Total records: {len(df)}")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    
    # Save processed data
    print("\n4. Saving processed data...")
    df.to_parquet(output_file)
    print(f"   Saved to: {output_file}")
    
    print("\n" + "=" * 60)
    print("Data preparation complete!")
    print("=" * 60)

def create_dummy_data(output_file):
    """Create dummy data for testing when real data is not available"""
    print("\nCreating dummy data...")
    
    # Generate time series
    start_date = pd.Timestamp('1995-07-01', tz='UTC')
    end_date = pd.Timestamp('1995-08-31 23:59:00', tz='UTC')
    dates = pd.date_range(start=start_date, end=end_date, freq='1s')
    
    # Generate traffic patterns
    np.random.seed(42)
    n = len(dates)
    
    data = []
    for i, ts in enumerate(dates):
        if i % 100000 == 0:
            print(f"  Generated {i}/{n} records...")
        
        # Skip hurricane period (Aug 1-3)
        if ts >= pd.Timestamp('1995-08-01 14:52:00', tz='UTC') and \
           ts <= pd.Timestamp('1995-08-03 04:36:00', tz='UTC'):
            continue
        
        # Generate realistic patterns
        hour_factor = np.sin(2 * np.pi * (ts.hour - 6) / 24)
        day_factor = 1.2 if ts.dayofweek < 5 else 0.8
        
        # Random requests based on patterns
        if np.random.random() < 0.15 * day_factor * max(0, hour_factor):
            data.append({
                'host': f'host_{np.random.randint(1, 1000)}',
                'request': 'GET /index.html HTTP/1.0',
                'status': np.random.choice([200, 304, 404], p=[0.7, 0.2, 0.1]),
                'bytes': np.random.randint(100, 50000)
            })
    
    df = pd.DataFrame(data, index=dates[:len(data)])
    df.index.name = 'timestamp'
    
    # Save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_parquet(output_file)
    
    print(f"\nDummy data created: {len(df)} records")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    main()
