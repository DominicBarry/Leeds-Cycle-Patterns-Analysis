import os
import pandas as pd
from datetime import datetime

def remove_negative_volumes(input_file, output_dir):
    """
    Removes all rows with negative Volume values and saves to a new CSV file
    
    Args:
        input_file (str): Path to the CSV file to process
        output_dir (str): Directory where the filtered file will be saved
    """
    print(f"Removing rows with negative Volume values from {os.path.basename(input_file)}...")
    
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
    
    # Check if Volume column exists
    if 'Volume' not in df.columns:
        print("Error: Volume column not found in the CSV file.")
        return
    
    # Convert Volume to numeric, handling non-numeric values
    print("Converting Volume to numeric values...")
    df['Volume_Numeric'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # Identify negative values
    negative_mask = df['Volume_Numeric'] < 0
    negative_count = negative_mask.sum()
    
    if negative_count == 0:
        print("No negative Volume values found in the dataset.")
        return
    
    print(f"Found {negative_count:,} rows with negative Volume values ({negative_count/len(df)*100:.4f}% of total).")
    
    # Remove rows with negative Volume values
    df_filtered = df[~negative_mask]
    
    # Drop the temporary numeric column
    df_filtered = df_filtered.drop(columns=['Volume_Numeric'])
    
    # Save the filtered dataframe to a new CSV file
    output_file = os.path.join(output_dir, f"leeds_cycle_counts_no_negatives_{timestamp}.csv")
    df_filtered.to_csv(output_file, index=False)
    
    print(f"Removed {negative_count:,} rows with negative Volume values.")
    print(f"Remaining rows: {len(df_filtered):,}")
    print(f"Filtered dataset saved to {output_file}")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path - updated to use the cleaned file
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts_deduplicated_20250227_125100.csv")
    
    # Output directory for filtered file
    output_dir = os.path.join(data_cleaning_dir, "cleaned-data")
    
    remove_negative_volumes(input_file, output_dir)