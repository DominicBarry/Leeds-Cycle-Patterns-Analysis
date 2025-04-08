import os
import pandas as pd
import numpy as np
from datetime import datetime

def verify_lane_direction(input_file, output_dir):
    """
    Verifies that LaneDirection column contains only numbers and identifies all unique values
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Verifying LaneDirection values in {os.path.basename(input_file)}...")
    
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
    
    # Check if LaneDirection column exists
    if 'LaneDirection' not in df.columns:
        print("Error: LaneDirection column not found in the CSV file.")
        return
    
    # Get value counts for LaneDirection
    lane_dir_counts = df['LaneDirection'].value_counts().sort_index()
    
    print(f"Found {len(lane_dir_counts)} unique values in LaneDirection column.")
    
    # Check if all values are numeric
    # First attempt to convert all values to numeric
    lane_dir_numeric = pd.to_numeric(df['LaneDirection'], errors='coerce')
    
    # Count non-numeric values (will be NaN after conversion)
    non_numeric_mask = lane_dir_numeric.isna() & ~df['LaneDirection'].isna()
    non_numeric_count = non_numeric_mask.sum()
    
    if non_numeric_count == 0:
        print("All non-null values in LaneDirection are numeric.")
    else:
        print(f"Warning: Found {non_numeric_count:,} non-numeric values in LaneDirection column.")
        
        # Get examples of non-numeric values
        non_numeric_values = df.loc[non_numeric_mask, 'LaneDirection'].unique()
        print("\nExamples of non-numeric values:")
        for i, val in enumerate(non_numeric_values[:10]):
            print(f"  {i+1}. '{val}' (type: {type(val).__name__})")
        
        # Save rows with non-numeric values
        non_numeric_rows = df[non_numeric_mask]
        non_numeric_file = os.path.join(output_dir, f"non_numeric_lane_directions_{timestamp}.csv")
        non_numeric_rows.to_csv(non_numeric_file, index=False)
        print(f"Rows with non-numeric LaneDirection values saved to {non_numeric_file}")
    
    # Display value counts
    print("\nUnique values in LaneDirection column:")
    print("-" * 40)
    print(f"{'Value':<10} {'Count':<12} {'Percentage':<10}")
    print("-" * 40)
    
    for value, count in lane_dir_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{value:<10} {count:<12,} {percentage:<10.2f}%")
    
    # Check for missing values
    missing_count = df['LaneDirection'].isnull().sum()
    if missing_count > 0:
        missing_percent = (missing_count / len(df)) * 100
        print(f"\nMissing values: {missing_count:,} ({missing_percent:.2f}%)")
    
    # Check relationship with DirectionDescription if it exists
    if 'DirectionDescription' in df.columns:
        print("\nAnalyzing relationship between LaneDirection and DirectionDescription...")
        
        # Create a cross-tabulation
        cross_tab = pd.crosstab(df['LaneDirection'], df['DirectionDescription'])
        
        # Save the cross-tabulation
        cross_tab_file = os.path.join(output_dir, f"lane_direction_description_crosstab_{timestamp}.csv")
        cross_tab.to_csv(cross_tab_file)
        print(f"Cross-tabulation saved to {cross_tab_file}")
        
        # Show the relationship
        relationship = df.groupby(['LaneDirection', 'DirectionDescription']).size().reset_index()
        relationship.columns = ['LaneDirection', 'DirectionDescription', 'Count']
        relationship = relationship.sort_values(['LaneDirection', 'Count'], ascending=[True, False])
        
        print("\nRelationship between LaneDirection and DirectionDescription:")
        for _, group in relationship.groupby('LaneDirection'):
            direction = group['LaneDirection'].iloc[0]
            print(f"\nLaneDirection {direction}:")
            
            for _, row in group.head(3).iterrows():
                print(f"  - {row['DirectionDescription']}: {row['Count']:,} occurrences")
            
            if len(group) > 3:
                print(f"  - (and {len(group) - 3} more descriptions...)")
    
    # Save detailed analysis to file
    lane_dir_analysis = pd.DataFrame({
        'LaneDirection': lane_dir_counts.index,
        'Count': lane_dir_counts.values,
        'Percentage': [(count / len(df)) * 100 for count in lane_dir_counts.values],
        'IsNumeric': [pd.to_numeric(val, errors='coerce') == val for val in lane_dir_counts.index]
    })
    
    analysis_file = os.path.join(output_dir, f"lane_direction_analysis_{timestamp}.csv")
    lane_dir_analysis.to_csv(analysis_file, index=False)
    print(f"\nDetailed LaneDirection analysis saved to {analysis_file}")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    verify_lane_direction(input_file, output_dir)