#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import time
import sys
import subprocess

def main():
    # Company CSV files directory
    company_dir = os.path.join('output', 'company')
    
    # Check if directory exists
    if not os.path.exists(company_dir):
        print(f"Error: Directory '{company_dir}' does not exist")
        return
    
    # Get all CSV files
    csv_files = glob.glob(os.path.join(company_dir, '*.csv'))
    
    if not csv_files:
        print(f"No CSV files found in '{company_dir}' directory")
        return
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    # Process each CSV file
    for i, csv_file in enumerate(csv_files):
        csv_name = os.path.basename(csv_file)
        print(f"\n[{i+1}/{len(csv_files)}] Processing: {csv_name}")
        
        # Build command (using list format to avoid injection attacks)
        command = [
            'python', 
            'extract_contact_info.py', 
            '--csv', csv_file, 
            '--url-column', 'Domain', 
            '--headless', 
            '--merge-results'
        ]
        print(f"Executing command: {' '.join(command)}")
        
        # Execute command (using subprocess.run instead of os.system for security)
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True)
        end_time = time.time()
        
        # Check command execution result
        if result.returncode == 0:
            print(f"✓ Successfully processed {csv_name}, Duration: {end_time - start_time:.2f} seconds")
        else:
            print(f"✗ Failed to process {csv_name}, Exit code: {result.returncode}")
            if result.stderr:
                print(f"  Error message: {result.stderr}")
        
        # Wait before processing the next file
        if i < len(csv_files) - 1:
            print("Waiting 5 seconds before processing the next file...")
            time.sleep(5)
    
    print(f"\nCompleted processing all {len(csv_files)} CSV files")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nUser interrupted, program exiting")
        sys.exit(1)
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1) 