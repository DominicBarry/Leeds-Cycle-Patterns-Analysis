import os
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_volume_outliers(input_file, output_dir, method='iqr', threshold=1.5):
    """
    Identifies outliers in Volume values and breaks down the results by year and calendar date
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
        method (str): Method for outlier detection ('iqr' or 'zscore')
        threshold (float): Threshold for outlier detection
    """
    print(f"Analyzing Volume outliers by year and calendar date in {os.path.basename(input_file)}...")
    print(f"Using method: {method}, threshold: {threshold}")
    
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
    
    # Convert Sdate to datetime
    print("Processing dates...")
    df['Date'] = pd.to_datetime(df['Sdate'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Extract date components
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Weekday'] = df['Date'].dt.weekday  # 0=Monday, 6=Sunday
    
    # Convert Volume to numeric, keeping only valid numeric values
    df['Volume_Numeric'] = pd.to_numeric(df['Volume'], errors='coerce')
    
    # Filter out NaN values for volume
    clean_df = df.dropna(subset=['Volume_Numeric'])
    print(f"Using {len(clean_df):,} records with valid numeric Volume values for analysis.")
    
    # Function to detect outliers
    def detect_outliers(data, method='iqr', threshold=1.5):
        if method == 'iqr':
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            return (data < lower_bound) | (data > upper_bound), lower_bound, upper_bound
        elif method == 'zscore':
            mean = data.mean()
            std = data.std()
            return (abs(data - mean) > threshold * std), mean - threshold * std, mean + threshold * std
        else:
            raise ValueError(f"Unknown method: {method}")
    
    # ---- Global Outlier Analysis ----
    print("\nPerforming global outlier analysis...")
    global_outlier_mask, global_lower, global_upper = detect_outliers(
        clean_df['Volume_Numeric'], method=method, threshold=threshold
    )
    
    global_outliers = clean_df[global_outlier_mask]
    global_outlier_count = len(global_outliers)
    global_outlier_percent = (global_outlier_count / len(clean_df)) * 100
    
    print(f"Global outlier thresholds: Lower = {global_lower:.2f}, Upper = {global_upper:.2f}")
    print(f"Found {global_outlier_count:,} global outliers ({global_outlier_percent:.2f}% of valid records).")
    
    # ---- Yearly Outlier Analysis ----
    print("\nAnalyzing outliers by year...")
    yearly_stats = []
    
    # For each year, calculate outliers
    for year in sorted(clean_df['Year'].unique()):
        year_data = clean_df[clean_df['Year'] == year]
        
        # Detect outliers for this year only
        year_outlier_mask, year_lower, year_upper = detect_outliers(
            year_data['Volume_Numeric'], method=method, threshold=threshold
        )
        
        year_outliers = year_data[year_outlier_mask]
        year_outlier_count = len(year_outliers)
        year_outlier_percent = (year_outlier_count / len(year_data)) * 100
        
        yearly_stats.append({
            'Year': year,
            'Total_Records': len(year_data),
            'Outlier_Count': year_outlier_count,
            'Outlier_Percentage': year_outlier_percent,
            'Lower_Threshold': year_lower,
            'Upper_Threshold': year_upper,
            'Min_Volume': year_data['Volume_Numeric'].min(),
            'Max_Volume': year_data['Volume_Numeric'].max(),
            'Mean_Volume': year_data['Volume_Numeric'].mean()
        })
    
    yearly_df = pd.DataFrame(yearly_stats)
    
    # Save yearly summary to file
    yearly_file = os.path.join(output_dir, f"volume_outliers_by_year_{timestamp}.csv")
    yearly_df.to_csv(yearly_file, index=False)
    print(f"Yearly outlier summary saved to {yearly_file}")
    
    # Display yearly summary
    print("\nOutlier summary by year:")
    print("-" * 80)
    print(f"{'Year':<6} {'Total':<10} {'Outliers':<10} {'Percentage':<10} {'Lower':<10} {'Upper':<10}")
    print("-" * 80)
    
    for _, row in yearly_df.iterrows():
        print(f"{int(row['Year']):<6} {row['Total_Records']:<10,} {row['Outlier_Count']:<10,} {row['Outlier_Percentage']:<10.2f}% {row['Lower_Threshold']:<10.2f} {row['Upper_Threshold']:<10.2f}")
    
    # ---- Monthly Outlier Analysis ----
    print("\nAnalyzing outliers by month...")
    monthly_stats = []
    
    # For each month, calculate outliers
    for month in range(1, 13):
        month_data = clean_df[clean_df['Month'] == month]
        
        if len(month_data) == 0:
            continue
        
        # Detect outliers for this month only
        month_outlier_mask, month_lower, month_upper = detect_outliers(
            month_data['Volume_Numeric'], method=method, threshold=threshold
        )
        
        month_outliers = month_data[month_outlier_mask]
        month_outlier_count = len(month_outliers)
        month_outlier_percent = (month_outlier_count / len(month_data)) * 100
        
        monthly_stats.append({
            'Month': month,
            'Month_Name': datetime(2000, month, 1).strftime('%B'),
            'Total_Records': len(month_data),
            'Outlier_Count': month_outlier_count,
            'Outlier_Percentage': month_outlier_percent,
            'Lower_Threshold': month_lower,
            'Upper_Threshold': month_upper
        })
    
    monthly_df = pd.DataFrame(monthly_stats)
    
    # Save monthly summary to file
    monthly_file = os.path.join(output_dir, f"volume_outliers_by_month_{timestamp}.csv")
    monthly_df.to_csv(monthly_file, index=False)
    print(f"Monthly outlier summary saved to {monthly_file}")
    
    # ---- Weekday Outlier Analysis ----
    print("\nAnalyzing outliers by day of week...")
    weekday_stats = []
    
    # For each weekday, calculate outliers
    for weekday in range(7):
        weekday_data = clean_df[clean_df['Weekday'] == weekday]
        
        if len(weekday_data) == 0:
            continue
        
        # Detect outliers for this weekday only
        weekday_outlier_mask, weekday_lower, weekday_upper = detect_outliers(
            weekday_data['Volume_Numeric'], method=method, threshold=threshold
        )
        
        weekday_outliers = weekday_data[weekday_outlier_mask]
        weekday_outlier_count = len(weekday_outliers)
        weekday_outlier_percent = (weekday_outlier_count / len(weekday_data)) * 100
        
        weekday_stats.append({
            'Weekday': weekday,
            'Weekday_Name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][weekday],
            'Total_Records': len(weekday_data),
            'Outlier_Count': weekday_outlier_count,
            'Outlier_Percentage': weekday_outlier_percent,
            'Lower_Threshold': weekday_lower,
            'Upper_Threshold': weekday_upper
        })
    
    weekday_df = pd.DataFrame(weekday_stats)
    
    # Save weekday summary to file
    weekday_file = os.path.join(output_dir, f"volume_outliers_by_weekday_{timestamp}.csv")
    weekday_df.to_csv(weekday_file, index=False)
    print(f"Weekday outlier summary saved to {weekday_file}")
    
    # ---- Save Global Outliers ----
    # Save all outliers to a file
    outliers_file = os.path.join(output_dir, f"volume_outliers_{timestamp}.csv")
    global_outliers.to_csv(outliers_file, index=False)
    print(f"\nAll outlier records saved to {outliers_file}")
    
    # Create a summary report with examples of top outliers
    top_high_outliers = global_outliers.nlargest(10, 'Volume_Numeric')
    top_low_outliers = global_outliers.nsmallest(10, 'Volume_Numeric')
    
    print("\nTop 10 highest Volume outliers:")
    print("-" * 70)
    for i, (_, row) in enumerate(top_high_outliers.iterrows(), 1):
        print(f"{i}. Date: {row['Date']}, Volume: {row['Volume_Numeric']}")
    
    print("\nTop 10 lowest Volume outliers:")
    print("-" * 70)
    for i, (_, row) in enumerate(top_low_outliers.iterrows(), 1):
        print(f"{i}. Date: {row['Date']}, Volume: {row['Volume_Numeric']}")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    # Run with IQR method (1.5 IQR threshold) - standard for box plots
    analyze_volume_outliers(input_file, output_dir, method='iqr', threshold=1.5)