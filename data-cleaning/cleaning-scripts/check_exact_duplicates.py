import os
import pandas as pd
from datetime import datetime

def check_exact_duplicates(input_file, output_dir):
    """
    Checks for exact duplicate rows in the dataset (all columns identical)
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Checking for exact duplicate rows in {os.path.basename(input_file)}...")
    
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
    
    # Identify duplicate rows
    print("\nChecking for exact duplicates...")
    
    # This will mark duplicates (keeping the first occurrence)
    duplicated_mask = df.duplicated(keep='first')
    duplicates = df[duplicated_mask]
    duplicate_count = len(duplicates)
    
    # Get all rows involved in duplication (including first occurrences)
    all_dupes_mask = df.duplicated(keep=False)
    all_dupes = df[all_dupes_mask]
    
    if duplicate_count > 0:
        print(f"Found {duplicate_count:,} exact duplicate rows ({duplicate_count/len(df)*100:.4f}% of total records).")
        print(f"These represent {len(all_dupes)/2:,} distinct records that appear twice in the dataset.")
        
        # Save duplicates to file (only the second+ occurrences)
        dup_file = os.path.join(output_dir, f"exact_duplicates_{timestamp}.csv")
        duplicates.to_csv(dup_file, index=False)
        print(f"Exact duplicates saved to {dup_file}")
        
        # Save all duplicate rows (including first occurrences) sorted to make pairs adjacent
        all_dupes_sorted = all_dupes.sort_values(by=list(df.columns))
        all_dupes_file = os.path.join(output_dir, f"all_duplicate_rows_{timestamp}.csv")
        all_dupes_sorted.to_csv(all_dupes_file, index=False)
        print(f"All rows involved in duplication saved to {all_dupes_file}")
        
        # Display a few examples
        print("\nExamples of exact duplicates (showing one pair):")
        
        # Get values from first duplicate
        first_dupe = duplicates.iloc[0]
        
        # Find all rows matching these values
        filter_condition = True
        for col, val in first_dupe.items():
            filter_condition = filter_condition & (df[col] == val)
        
        # Display the duplicate pair
        print(df[filter_condition].to_string())
    else:
        print("No exact duplicate rows found.")
    
    print("\nDuplicate analysis complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    check_exact_duplicates(input_file, output_dir)