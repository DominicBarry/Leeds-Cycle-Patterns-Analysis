import os
import pandas as pd
import numpy as np
from datetime import datetime

def verify_volume_values(input_file, output_dir):
    """
    Verifies that Volume column contains only numeric values and shows top/bottom 5 values with counts
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Verifying Volume values in {os.path.basename(input_file)}...")
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate timestamp for output files
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
    
    # Check if all values are numeric
    volume_numeric = pd.to_numeric(df['Volume'], errors='coerce')
    non_numeric_mask = volume_numeric.isna() & ~df['Volume'].isna()
    non_numeric_count = non_numeric_mask.sum()
    
    if non_numeric_count == 0:
        print("All non-null values in Volume are numeric.")
    else:
        print(f"Warning: Found {non_numeric_count:,} non-numeric values in Volume column.")
        
        # Get examples of non-numeric values
        non_numeric_rows = df[non_numeric_mask]
        non_numeric_values = non_numeric_rows['Volume'].unique()
        
        print("\nExamples of non-numeric values:")
        for i, val in enumerate(non_numeric_values[:10]):
            print(f"  {i+1}. '{val}' (type: {type(val).__name__})")
        
        # Save non-numeric rows to file
        non_numeric_file = os.path.join(output_dir, f"non_numeric_volumes_{timestamp}.csv")
        non_numeric_rows.to_csv(non_numeric_file, index=False)
        print(f"Rows with non-numeric Volume values saved to {non_numeric_file}")
    
    # Get value counts for numeric values
    numeric_df = df[~non_numeric_mask]
    numeric_df['Volume_Numeric'] = pd.to_numeric(numeric_df['Volume'])
    
    # Count occurrences of each value
    value_counts = numeric_df['Volume_Numeric'].value_counts().sort_index()
    
    print(f"\nFound {len(value_counts)} unique numeric values in Volume column.")
    
    # Get top 5 and bottom 5 values by frequency
    top_values = value_counts.nlargest(5)
    bottom_values = value_counts.nsmallest(5)
    
    # Display top values
    print("\nTop 5 most common Volume values:")
    print("-" * 40)
    print(f"{'Value':<10} {'Count':<12} {'Percentage':<10}")
    print("-" * 40)
    
    for value, count in top_values.items():
        percentage = (count / len(numeric_df)) * 100
        print(f"{value:<10} {count:<12,} {percentage:<10.2f}%")
    
    # Display bottom values
    print("\nBottom 5 least common Volume values:")
    print("-" * 40)
    print(f"{'Value':<10} {'Count':<12} {'Percentage':<10}")
    print("-" * 40)
    
    for value, count in bottom_values.items():
        percentage = (count / len(numeric_df)) * 100
        print(f"{value:<10} {count:<12,} {percentage:<10.2f}%")
    
    # Get top 5 and bottom 5 values by magnitude
    top_magnitude = numeric_df['Volume_Numeric'].nlargest(5)
    bottom_magnitude = numeric_df['Volume_Numeric'].nsmallest(5)
    
    # Display top magnitude values
    print("\nTop 5 highest Volume values:")
    print("-" * 25)
    print(f"{'Rank':<5} {'Value':<10}")
    print("-" * 25)
    
    for i, value in enumerate(top_magnitude):
        print(f"{i+1:<5} {value:<10}")
    
    # Display bottom magnitude values
    print("\nBottom 5 lowest Volume values:")
    print("-" * 25)
    print(f"{'Rank':<5} {'Value':<10}")
    print("-" * 25)
    
    for i, value in enumerate(bottom_magnitude):
        print(f"{i+1:<5} {value:<10}")
    
    # Check for missing values
    missing_count = df['Volume'].isnull().sum()
    if missing_count > 0:
        missing_percent = (missing_count / len(df)) * 100
        print(f"\nMissing values: {missing_count:,} ({missing_percent:.2f}%)")
    
    # Check for zeros
    zero_count = (numeric_df['Volume_Numeric'] == 0).sum()
    if zero_count > 0:
        zero_percent = (zero_count / len(numeric_df)) * 100
        print(f"Zero values: {zero_count:,} ({zero_percent:.2f}%)")
    
    # Check for negative values
    negative_count = (numeric_df['Volume_Numeric'] < 0).sum()
    if negative_count > 0:
        negative_percent = (negative_count / len(numeric_df)) * 100
        print(f"Negative values: {negative_count:,} ({negative_percent:.2f}%)")
        
        # Save negative values to file
        negative_rows = numeric_df[numeric_df['Volume_Numeric'] < 0]
        negative_file = os.path.join(output_dir, f"negative_volumes_{timestamp}.csv")
        negative_rows.to_csv(negative_file, index=False)
        print(f"Rows with negative Volume values saved to {negative_file}")
    
    # Calculate summary statistics
    print("\nSummary statistics for Volume:")
    stats = numeric_df['Volume_Numeric'].describe()
    print(f"Count:      {stats['count']:,}")
    print(f"Mean:       {stats['mean']:.2f}")
    print(f"Std Dev:    {stats['std']:.2f}")
    print(f"Min:        {stats['min']}")
    print(f"25th Perc:  {stats['25%']}")
    print(f"Median:     {stats['50%']}")
    print(f"75th Perc:  {stats['75%']}")
    print(f"Max:        {stats['max']}")
    
    # Save full value counts to file
    value_counts_df = pd.DataFrame({
        'Volume': value_counts.index,
        'Count': value_counts.values,
        'Percentage': [(count / len(numeric_df)) * 100 for count in value_counts.values]
    })
    
    counts_file = os.path.join(output_dir, f"volume_value_counts_{timestamp}.csv")
    value_counts_df.to_csv(counts_file, index=False)
    print(f"\nComplete Volume value counts saved to {counts_file}")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    verify_volume_values(input_file, output_dir)