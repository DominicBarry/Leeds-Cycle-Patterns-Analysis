import os
import pandas as pd
from datetime import datetime

def remove_exact_duplicates(input_file, output_dir):
    """
    Removes exact duplicate rows from the dataset and saves to a new CSV file
    
    Args:
        input_file (str): Path to the CSV file to process
        output_dir (str): Directory where the deduplicated file will be saved
    """
    print(f"Removing exact duplicate rows from {os.path.basename(input_file)}...")
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Generate timestamp for output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load the CSV file
    try:
        print("Loading data...")
        df = pd.read_csv(input_file, low_memory=False)
        print(f"File loaded successfully with {len(df):,} rows.")
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return
    
    # Identify duplicate rows
    print("Checking for exact duplicates...")
    duplicated_mask = df.duplicated()
    duplicate_count = duplicated_mask.sum()
    
    if duplicate_count == 0:
        print("No exact duplicate rows found in the dataset.")
        return
    
    print(f"Found {duplicate_count:,} exact duplicate rows ({duplicate_count/len(df)*100:.4f}% of total).")
    
    # Remove duplicates (keeping the first occurrence)
    df_deduplicated = df.drop_duplicates()
    
    # Save the deduplicated dataframe to a new CSV file
    output_file = os.path.join(output_dir, f"leeds_cycle_counts_deduplicated_{timestamp}.csv")
    df_deduplicated.to_csv(output_file, index=False)
    
    print(f"Removed {duplicate_count:,} duplicate rows.")
    print(f"Original row count: {len(df):,}")
    print(f"New row count: {len(df_deduplicated):,}")
    print(f"Deduplicated dataset saved to {output_file}")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for deduplicated file
    output_dir = os.path.join(data_cleaning_dir, "cleaned-data")
    
    remove_exact_duplicates(input_file, output_dir)