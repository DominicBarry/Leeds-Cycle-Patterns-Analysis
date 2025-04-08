import os
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_negative_volumes_by_year(input_file, output_dir):
    """
    Analyzes negative Volume values and breaks down the results by year
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Analyzing negative Volume values by year in {os.path.basename(input_file)}...")
    
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
    
    # Check if required columns exist
    if 'Volume' not in df.columns:
        print("Error: Volume column not found in the CSV file.")
        return
    if 'Sdate' not in df.columns:
        print("Error: Sdate column not found in the CSV file.")
        return
    
    # Extract year from Sdate
    print("Extracting year from Sdate...")
    df['Year'] = pd.to_datetime(df['Sdate'], format='%d/%m/%Y %H:%M', errors='coerce').dt.year
    
    # Convert Volume to numeric, keeping only valid numeric values
    df['Volume_Numeric'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # Find negative volumes
    negative_mask = df['Volume_Numeric'] < 0
    negative_count = negative_mask.sum()
    
    if negative_count == 0:
        print("No negative Volume values found in the dataset.")
        return
    
    print(f"\nFound {negative_count:,} negative Volume values ({negative_count/len(df)*100:.4f}% of total records).")
    
    # Get negative volume records
    negative_df = df[negative_mask]
    
    # Breakdown by year
    yearly_counts = negative_df.groupby('Year').size()
    yearly_totals = df.groupby('Year').size()
    yearly_percentages = (yearly_counts / yearly_totals) * 100
    
    # Create summary table
    summary = pd.DataFrame({
        'Total_Records': yearly_totals,
        'Negative_Records': yearly_counts,
        'Percentage': yearly_percentages
    })
    
    # Save summary to file
    summary_file = os.path.join(output_dir, f"negative_volumes_by_year_{timestamp}.csv")
    summary.to_csv(summary_file)
    print(f"Negative volumes summary by year saved to {summary_file}")
    
    # Display summary
    print("\nBreakdown of negative Volume values by year:")
    print("-" * 70)
    print(f"{'Year':<10} {'Total Records':<15} {'Negative Records':<20} {'Percentage':<10}")
    print("-" * 70)
    
    for year, row in summary.iterrows():
        print(f"{year:<10} {row['Total_Records']:<15,} {row['Negative_Records']:<20,} {row['Percentage']:<10.4f}%")
    
    # Calculate statistics on negative values
    print("\nStatistics on negative Volume values:")
    neg_stats = negative_df['Volume_Numeric'].describe()
    print(f"Count:      {neg_stats['count']:,}")
    print(f"Mean:       {neg_stats['mean']:.2f}")
    print(f"Std Dev:    {neg_stats['std']:.2f}")
    print(f"Min:        {neg_stats['min']}")
    print(f"25th Perc:  {neg_stats['25%']}")
    print(f"Median:     {neg_stats['50%']}")
    print(f"75th Perc:  {neg_stats['75%']}")
    print(f"Max:        {neg_stats['max']}")
    
    # Check if Flag Text column exists
    flag_column = None
    for col in df.columns:
        if 'flag' in col.lower() and 'text' in col.lower():
            flag_column = col
            break
    
    # Analyze relationship with Flag Text if it exists
    if flag_column:
        print(f"\nAnalyzing relationship between negative Volume values and {flag_column}...")
        
        # Count flag text values for negative volumes
        neg_flags = negative_df[flag_column].value_counts()
        
        print(f"\nTop Flag Text values associated with negative Volume values:")
        print("-" * 70)
        print(f"{'Flag Text':<40} {'Count':<10} {'Percentage':<10}")
        print("-" * 70)
        
        for flag, count in neg_flags.head(10).items():
            percentage = (count / negative_count) * 100
            flag_str = str(flag)
            if len(flag_str) > 37:
                flag_str = flag_str[:34] + "..."
            print(f"{flag_str:<40} {count:<10,} {percentage:<10.2f}%")
    
    # Save all negative volume records to file
    negative_file = os.path.join(output_dir, f"negative_volume_records_{timestamp}.csv")
    negative_df.to_csv(negative_file, index=False)
    print(f"\nAll negative Volume records saved to {negative_file}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    analyze_negative_volumes_by_year(input_file, output_dir)