import os
import pandas as pd
from datetime import datetime

def verify_lane_descriptions(input_file, output_dir):
    """
    Verifies that all values in LaneDescription column are strings
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Verifying LaneDescription values in {os.path.basename(input_file)}...")
    
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
    
    # Check if LaneDescription column exists
    if 'LaneDescription' not in df.columns:
        print("Error: LaneDescription column not found in the CSV file.")
        return
    
    # Get value counts for data types
    df_types = df['LaneDescription'].map(lambda x: type(x).__name__)
    type_counts = df_types.value_counts()
    
    print("\nData types found in LaneDescription column:")
    for dtype, count in type_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {dtype}: {count:,} values ({percentage:.2f}%)")
    
    # Check if all non-null values are strings
    all_strings = df['LaneDescription'].map(lambda x: isinstance(x, str) or pd.isna(x)).all()
    
    if all_strings:
        print("\nAll non-null values in LaneDescription are strings.")
    else:
        print("\nWarning: Not all values in LaneDescription are strings!")
        
        # Find non-string values
        non_string_rows = df[~df['LaneDescription'].map(lambda x: isinstance(x, str) or pd.isna(x))]
        
        # Save the non-string rows to a file
        non_string_file = os.path.join(output_dir, f"non_string_lane_descriptions_{timestamp}.csv")
        non_string_rows.to_csv(non_string_file, index=False)
        print(f"Rows with non-string LaneDescription values saved to {non_string_file}")
        
        # Display examples
        print("\nExamples of non-string values:")
        for i, (idx, row) in enumerate(non_string_rows.head(5).iterrows()):
            print(f"  {i+1}. Value: {row['LaneDescription']}, Type: {type(row['LaneDescription']).__name__}")
    
    # Get unique values and their frequencies
    value_counts = df['LaneDescription'].value_counts()
    
    print(f"\nFound {len(value_counts)} unique values in LaneDescription column.")
    
    # Display the top 10 most common values
    print("\nTop 10 most common LaneDescription values:")
    for value, count in value_counts.head(10).items():
        percentage = (count / len(df)) * 100
        if isinstance(value, str):
            print(f"  '{value}': {count:,} occurrences ({percentage:.2f}%)")
        else:
            print(f"  {value} (type: {type(value).__name__}): {count:,} occurrences ({percentage:.2f}%)")
    
    # Check for missing values
    missing_count = df['LaneDescription'].isnull().sum()
    if missing_count > 0:
        missing_percent = (missing_count / len(df)) * 100
        print(f"\nMissing values: {missing_count:,} ({missing_percent:.2f}%)")
    
    # Check for blank strings
    blank_count = (df['LaneDescription'] == '').sum()
    if blank_count > 0:
        blank_percent = (blank_count / len(df)) * 100
        print(f"Blank strings: {blank_count:,} ({blank_percent:.2f}%)")
    
    # Save detailed analysis to file
    lane_desc_analysis = pd.DataFrame({
        'LaneDescription': value_counts.index,
        'Count': value_counts.values,
        'Percentage': [(count / len(df)) * 100 for count in value_counts.values],
        'DataType': [type(val).__name__ for val in value_counts.index]
    })
    
    analysis_file = os.path.join(output_dir, f"lane_description_analysis_{timestamp}.csv")
    lane_desc_analysis.to_csv(analysis_file, index=False)
    print(f"\nDetailed LaneDescription analysis saved to {analysis_file}")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    verify_lane_descriptions(input_file, output_dir)