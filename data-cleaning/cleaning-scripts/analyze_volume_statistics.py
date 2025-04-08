import os
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_volume_statistics(input_file, output_dir):
    """
    Generates comprehensive summary statistics for the Volume column
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Generating Volume summary statistics for {os.path.basename(input_file)}...")
    
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
    
    # Convert Volume to numeric, handling non-numeric values
    print("Converting Volume to numeric values...")
    df['Volume_Numeric'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # Filter out non-numeric values
    valid_volume_df = df.dropna(subset=['Volume_Numeric'])
    
    print(f"Found {len(valid_volume_df):,} records with valid numeric Volume values.")
    print(f"Found {len(df) - len(valid_volume_df):,} records with non-numeric or missing Volume values.")
    
    # Basic statistics for the entire dataset
    stats = valid_volume_df['Volume_Numeric'].describe(percentiles=[0.01, 0.05, 0.10, 0.25, 0.5, 0.75, 0.90, 0.95, 0.99])
    
    # Add additional statistics
    stats_dict = stats.to_dict()
    stats_dict['mode'] = valid_volume_df['Volume_Numeric'].mode()[0]
    stats_dict['range'] = stats_dict['max'] - stats_dict['min']
    stats_dict['iqr'] = stats_dict['75%'] - stats_dict['25%']
    stats_dict['skewness'] = valid_volume_df['Volume_Numeric'].skew()
    stats_dict['kurtosis'] = valid_volume_df['Volume_Numeric'].kurt()
    stats_dict['zeros'] = (valid_volume_df['Volume_Numeric'] == 0).sum()
    stats_dict['zeros_percentage'] = (stats_dict['zeros'] / len(valid_volume_df)) * 100
    stats_dict['negative_values'] = (valid_volume_df['Volume_Numeric'] < 0).sum()
    stats_dict['negative_percentage'] = (stats_dict['negative_values'] / len(valid_volume_df)) * 100
    
    # Print basic statistics
    print("\nVolume Summary Statistics:")
    print("-" * 50)
    print(f"Count:               {stats_dict['count']:,.0f}")
    print(f"Mean:                {stats_dict['mean']:.2f}")
    print(f"Median (50th perc):  {stats_dict['50%']:.2f}")
    print(f"Mode:                {stats_dict['mode']:.2f}")
    print(f"Standard Deviation:  {stats_dict['std']:.2f}")
    print(f"Minimum:             {stats_dict['min']:.2f}")
    print(f"Maximum:             {stats_dict['max']:.2f}")
    print(f"Range:               {stats_dict['range']:.2f}")
    print(f"Interquartile Range: {stats_dict['iqr']:.2f}")
    print(f"Skewness:            {stats_dict['skewness']:.2f}")
    print(f"Kurtosis:            {stats_dict['kurtosis']:.2f}")
    
    # Print additional statistics
    print("\nPercentiles:")
    print(f"1st percentile:      {stats_dict['1%']:.2f}")
    print(f"5th percentile:      {stats_dict['5%']:.2f}")
    print(f"10th percentile:     {stats_dict['10%']:.2f}")
    print(f"25th percentile:     {stats_dict['25%']:.2f}")
    print(f"75th percentile:     {stats_dict['75%']:.2f}")
    print(f"90th percentile:     {stats_dict['90%']:.2f}")
    print(f"95th percentile:     {stats_dict['95%']:.2f}")
    print(f"99th percentile:     {stats_dict['99%']:.2f}")
    
    # Print zero and negative value statistics
    print("\nZeros and Negative Values:")
    print(f"Zero values:         {stats_dict['zeros']:,} ({stats_dict['zeros_percentage']:.2f}%)")
    print(f"Negative values:     {stats_dict['negative_values']:,} ({stats_dict['negative_percentage']:.2f}%)")
    
    # Calculate frequency distribution
    bins = [0, 1, 5, 10, 25, 50, 100, 250, 500, 1000, float('inf')]
    labels = ['0-1', '1-5', '5-10', '10-25', '25-50', '50-100', '100-250', '250-500', '500-1000', '1000+']
    
    # Handle negative values by creating a separate bin
    positive_df = valid_volume_df[valid_volume_df['Volume_Numeric'] >= 0]
    negative_count = len(valid_volume_df) - len(positive_df)
    
    # Create binned distribution for positive values
    positive_df['Volume_Bin'] = pd.cut(positive_df['Volume_Numeric'], bins=bins, labels=labels)
    bin_counts = positive_df['Volume_Bin'].value_counts().sort_index()
    
    # Add negative bin
    if negative_count > 0:
        bin_counts = pd.concat([pd.Series([negative_count], index=['Negative']), bin_counts])
    
    # Calculate percentages
    bin_percentages = (bin_counts / len(valid_volume_df)) * 100
    
    # Display distribution
    print("\nVolume Distribution:")
    print("-" * 50)
    print(f"{'Range':<10} {'Count':<10} {'Percentage':<10}")
    print("-" * 50)
    
    for bin_range, count in bin_counts.items():
        percentage = bin_percentages[bin_range]
        print(f"{bin_range:<10} {count:<10,} {percentage:<10.2f}%")
    
    # Break down by year if Sdate column exists
    if 'Sdate' in df.columns:
        print("\nExtracting year from Sdate for yearly statistics...")
        df['Year'] = pd.to_datetime(df['Sdate'], format='%d/%m/%Y %H:%M', errors='coerce').dt.year
        
        # Group by year and calculate statistics
        yearly_stats = []
        
        for year in sorted(df['Year'].dropna().unique()):
            year_data = valid_volume_df[valid_volume_df['Year'] == year]
            
            if len(year_data) == 0:
                continue
                
            year_stats = {
                'Year': year,
                'Count': len(year_data),
                'Mean': year_data['Volume_Numeric'].mean(),
                'Median': year_data['Volume_Numeric'].median(),
                'Std_Dev': year_data['Volume_Numeric'].std(),
                'Min': year_data['Volume_Numeric'].min(),
                'Max': year_data['Volume_Numeric'].max(),
                'Zero_Count': (year_data['Volume_Numeric'] == 0).sum(),
                'Zero_Percentage': ((year_data['Volume_Numeric'] == 0).sum() / len(year_data)) * 100,
                'Negative_Count': (year_data['Volume_Numeric'] < 0).sum(),
                'Negative_Percentage': ((year_data['Volume_Numeric'] < 0).sum() / len(year_data)) * 100
            }
            
            yearly_stats.append(year_stats)
        
        yearly_df = pd.DataFrame(yearly_stats)
        
        # Display yearly statistics
        print("\nYearly Volume Statistics:")
        print("-" * 100)
        print(f"{'Year':<6} {'Count':<10} {'Mean':<8} {'Median':<8} {'Std Dev':<8} {'Min':<8} {'Max':<8} {'Zero %':<8} {'Neg %':<8}")
        print("-" * 100)
        
        for _, row in yearly_df.iterrows():
            print(f"{int(row['Year']):<6} {row['Count']:<10,} {row['Mean']:<8.2f} {row['Median']:<8.2f} {row['Std_Dev']:<8.2f} {row['Min']:<8.2f} {row['Max']:<8.2f} {row['Zero_Percentage']:<8.2f} {row['Negative_Percentage']:<8.2f}")
        
        # Save yearly statistics
        yearly_file = os.path.join(output_dir, f"volume_yearly_stats_{timestamp}.csv")
        yearly_df.to_csv(yearly_file, index=False)
        print(f"\nYearly Volume statistics saved to {yearly_file}")
    
    # Save overall statistics
    stats_df = pd.Series(stats_dict).reset_index()
    stats_df.columns = ['Statistic', 'Value']
    
    stats_file = os.path.join(output_dir, f"volume_statistics_{timestamp}.csv")
    stats_df.to_csv(stats_file, index=False)
    print(f"Overall Volume statistics saved to {stats_file}")
    
    # Save distribution
    dist_df = pd.DataFrame({
        'Range': bin_counts.index,
        'Count': bin_counts.values,
        'Percentage': bin_percentages.values
    })
    
    dist_file = os.path.join(output_dir, f"volume_distribution_{timestamp}.csv")
    dist_df.to_csv(dist_file, index=False)
    print(f"Volume distribution saved to {dist_file}")
    
    print("\nStatistical analysis complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    analyze_volume_statistics(input_file, output_dir)