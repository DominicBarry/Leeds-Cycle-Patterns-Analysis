import os
import pandas as pd
from datetime import datetime

def remove_specific_outlier(input_file, output_dir, outlier_value=5641):
    """
    Removes the specific row with Volume value equal to the outlier_value
    
    Args:
        input_file (str): Path to the CSV file to process
        output_dir (str): Directory where the filtered file will be saved
        outlier_value (int): The specific Volume value to remove
    """
    print(f"Removing row with Volume value of {outlier_value} from {os.path.basename(input_file)}...")
    
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
    
    # Identify the outlier row
    outlier_mask = df['Volume_Numeric'] == outlier_value
    outlier_count = outlier_mask.sum()
    
    if outlier_count == 0:
        print(f"No rows found with Volume value of {outlier_value}.")
        return
    
    print(f"Found {outlier_count:,} rows with Volume value of {outlier_value}.")
    
    # Display the outlier row(s) for verification
    print("\nOutlier row(s) to be removed:")
    print(df[outlier_mask])
    
    # Remove the outlier row(s)
    df_filtered = df[~outlier_mask]
    
    # Drop the temporary numeric column
    df_filtered = df_filtered.drop(columns=['Volume_Numeric'])
    
    # Save the filtered dataframe to a new CSV file
    output_file = os.path.join(output_dir, f"leeds_cycle_counts_no_outlier_{timestamp}.csv")
    df_filtered.to_csv(output_file, index=False)
    
    print(f"\nRemoved {outlier_count:,} row(s) with Volume value of {outlier_value}.")
    print(f"Remaining rows: {len(df_filtered):,}")
    print(f"Filtered dataset saved to {output_file}")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts_no_negatives_20250227_125328.csv")
    
    # Output directory for filtered file
    output_dir = os.path.join(data_cleaning_dir, "cleaned-data")
    
    # Remove the specific outlier
    remove_specific_outlier(input_file, output_dir, outlier_value=5641)