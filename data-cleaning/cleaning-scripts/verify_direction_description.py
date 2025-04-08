import os
import pandas as pd
from datetime import datetime

def verify_direction_description(input_file, output_dir):
    """
    Verifies that DirectionDescription column contains only string values and identifies all unique values
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Verifying DirectionDescription values in {os.path.basename(input_file)}...")
    
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
    
    # Check if DirectionDescription column exists
    if 'DirectionDescription' not in df.columns:
        print("Error: DirectionDescription column not found in the CSV file.")
        return
    
    # Get value counts for DirectionDescription
    dir_desc_counts = df['DirectionDescription'].value_counts().sort_index()
    
    print(f"Found {len(dir_desc_counts)} unique values in DirectionDescription column.")
    
    # Check if all values are strings
    non_string_mask = ~df['DirectionDescription'].map(lambda x: isinstance(x, str) or pd.isna(x))
    non_string_count = non_string_mask.sum()
    
    if non_string_count == 0:
        print("All non-null values in DirectionDescription are strings.")
    else:
        print(f"Warning: Found {non_string_count:,} non-string values in DirectionDescription column.")
        
        # Get examples of non-string values
        non_string_values = df.loc[non_string_mask, 'DirectionDescription'].unique()
        print("\nExamples of non-string values:")
        for i, val in enumerate(non_string_values[:10]):
            print(f"  {i+1}. {val} (type: {type(val).__name__})")
        
        # Save rows with non-string values
        non_string_rows = df[non_string_mask]
        non_string_file = os.path.join(output_dir, f"non_string_direction_descriptions_{timestamp}.csv")
        non_string_rows.to_csv(non_string_file, index=False)
        print(f"Rows with non-string DirectionDescription values saved to {non_string_file}")
    
    # Display value counts
    print("\nUnique values in DirectionDescription column:")
    print("-" * 70)
    print(f"{'Value':<30} {'Count':<12} {'Percentage':<10}")
    print("-" * 70)
    
    for value, count in dir_desc_counts.items():
        percentage = (count / len(df)) * 100
        display_value = str(value)
        if len(display_value) > 27:
            display_value = display_value[:24] + "..."
        print(f"{display_value:<30} {count:<12,} {percentage:<10.2f}%")
    
    # Check for missing values
    missing_count = df['DirectionDescription'].isnull().sum()
    if missing_count > 0:
        missing_percent = (missing_count / len(df)) * 100
        print(f"\nMissing values: {missing_count:,} ({missing_percent:.2f}%)")
    
    # Check for blank strings
    blank_count = (df['DirectionDescription'] == '').sum()
    if blank_count > 0:
        blank_percent = (blank_count / len(df)) * 100
        print(f"Blank strings: {blank_count:,} ({blank_percent:.2f}%)")
    
    # Check relationship with LaneDirection if it exists
    if 'LaneDirection' in df.columns:
        print("\nAnalyzing relationship between DirectionDescription and LaneDirection...")
        
        # Create a cross-tabulation
        cross_tab = pd.crosstab(df['DirectionDescription'], df['LaneDirection'])
        
        # Save the cross-tabulation
        cross_tab_file = os.path.join(output_dir, f"direction_description_lane_direction_crosstab_{timestamp}.csv")
        cross_tab.to_csv(cross_tab_file)
        print(f"Cross-tabulation saved to {cross_tab_file}")
        
        # Show the relationship
        relationship = df.groupby(['DirectionDescription', 'LaneDirection']).size().reset_index()
        relationship.columns = ['DirectionDescription', 'LaneDirection', 'Count']
        relationship = relationship.sort_values(['DirectionDescription', 'Count'], ascending=[True, False])
        
        print("\nSample relationship between DirectionDescription and LaneDirection:")
        for i, (description, group) in enumerate(relationship.groupby('DirectionDescription')):
            if i >= 5:  # Limit to 5 descriptions to keep output manageable
                remaining = len(relationship.groupby('DirectionDescription')) - 5
                print(f"\n(and {remaining} more descriptions...)")
                break
                
            print(f"\nDirectionDescription '{description}':")
            
            for _, row in group.head(2).iterrows():
                print(f"  - LaneDirection {row['LaneDirection']}: {row['Count']:,} occurrences")
            
            if len(group) > 2:
                print(f"  - (and {len(group) - 2} more lane directions...)")
    
    # Save detailed analysis to file
    dir_desc_analysis = pd.DataFrame({
        'DirectionDescription': dir_desc_counts.index,
        'Count': dir_desc_counts.values,
        'Percentage': [(count / len(df)) * 100 for count in dir_desc_counts.values],
        'IsString': [isinstance(val, str) for val in dir_desc_counts.index]
    })
    
    analysis_file = os.path.join(output_dir, f"direction_description_analysis_{timestamp}.csv")
    dir_desc_analysis.to_csv(analysis_file, index=False)
    print(f"\nDetailed DirectionDescription analysis saved to {analysis_file}")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    verify_direction_description(input_file, output_dir)