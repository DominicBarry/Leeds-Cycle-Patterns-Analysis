import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

def analyze_recording_completeness(input_file, output_dir):
    """
    Analyzes the recording completeness by calculating, for each year and Cosit,
    the percentage of days where data was recorded for all 24 hours
    
    Args:
        input_file (str): Path to the CSV file to analyze
        output_dir (str): Directory where the results will be saved
    """
    print(f"Analyzing recording completeness in {os.path.basename(input_file)}...")
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Load the CSV file
    try:
        print("Loading data...")
        df = pd.read_csv(input_file, low_memory=False)
        print(f"File loaded successfully with {len(df):,} rows and {len(df.columns)} columns.")
    except Exception as e:
        print(f"Error loading file: {str(e)}")
        return
    
    # Check if required columns exist
    if 'Sdate' not in df.columns or 'Cosit' not in df.columns:
        print("Error: Required columns (Sdate and/or Cosit) not found in the CSV file.")
        return
    
    # Convert Sdate to datetime
    print("Converting dates...")
    df['DateTime'] = pd.to_datetime(df['Sdate'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Extract date components
    df['Date'] = df['DateTime'].dt.date
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    df['Day'] = df['DateTime'].dt.day
    df['Hour'] = df['DateTime'].dt.hour
    
    # Filter out rows with invalid dates
    df = df.dropna(subset=['DateTime'])
    
    print("Analyzing data completeness...")
    
    # Get unique years, Cosits, and dates
    years = sorted(df['Year'].unique())
    cosits = sorted(df['Cosit'].unique())
    
    # Create a list to store results
    results = []
    
    # Helper function to get days in year (accounting for leap years)
    def days_in_year(year):
        return 366 if calendar.isleap(year) else 365
    
    # Process each Cosit and year
    print(f"Processing {len(cosits)} Cosits across {len(years)} years...")
    
    for cosit in cosits:
        cosit_data = df[df['Cosit'] == cosit]
        
        for year in years:
            # Skip if this Cosit has no data for this year
            if year not in cosit_data['Year'].unique():
                continue
            
            year_data = cosit_data[cosit_data['Year'] == year]
            
            # Get all unique dates for this Cosit and year
            dates = year_data['Date'].unique()
            
            # Calculate total possible days in this year
            total_days = days_in_year(year)
            
            # For current year, adjust total days to those elapsed so far
            if year == datetime.now().year:
                total_days = (datetime.now().date() - datetime(year, 1, 1).date()).days + 1
            
            # Count days with complete 24-hour coverage
            complete_days = 0
            incomplete_days = 0
            missing_days = total_days - len(dates)
            
            for date in dates:
                day_data = year_data[year_data['Date'] == date]
                hours_recorded = day_data['Hour'].nunique()
                
                if hours_recorded == 24:
                    complete_days += 1
                else:
                    incomplete_days += 1
            
            # Calculate percentages
            days_with_any_data = len(dates)
            days_with_complete_data = complete_days
            
            percent_days_recorded = (days_with_any_data / total_days) * 100
            percent_complete_days = (days_with_complete_data / total_days) * 100
            percent_days_complete_when_recorded = (days_with_complete_data / days_with_any_data) * 100 if days_with_any_data > 0 else 0
            
            # Store results
            results.append({
                'Cosit': cosit,
                'Year': year,
                'Total_Days_In_Year': total_days,
                'Days_With_Any_Data': days_with_any_data,
                'Days_With_Complete_Data': days_with_complete_data,
                'Days_With_Incomplete_Data': incomplete_days,
                'Days_With_No_Data': missing_days,
                'Percent_Days_Recorded': percent_days_recorded,
                'Percent_Complete_Days': percent_complete_days,
                'Percent_Days_Complete_When_Recorded': percent_days_complete_when_recorded
            })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save detailed results
    output_file = os.path.join(output_dir, f"recording_completeness_corrected_{timestamp}.csv")
    results_df.to_csv(output_file, index=False)
    print(f"\nDetailed recording completeness saved to {output_file}")
    
    # Create summary by year
    yearly_summary = results_df.groupby('Year').agg({
        'Total_Days_In_Year': 'first',
        'Days_With_Any_Data': 'sum',
        'Days_With_Complete_Data': 'sum',
        'Days_With_Incomplete_Data': 'sum',
        'Days_With_No_Data': 'sum'
    })
    
    # Calculate percentages for yearly summary
    yearly_summary['Total_Possible_Days'] = yearly_summary['Total_Days_In_Year'] * len(cosits)
    yearly_summary['Percent_Days_Recorded'] = (yearly_summary['Days_With_Any_Data'] / yearly_summary['Total_Possible_Days']) * 100
    yearly_summary['Percent_Complete_Days'] = (yearly_summary['Days_With_Complete_Data'] / yearly_summary['Total_Possible_Days']) * 100
    
    # Save yearly summary
    yearly_file = os.path.join(output_dir, f"yearly_completeness_summary_{timestamp}.csv")
    yearly_summary.to_csv(yearly_file)
    print(f"Yearly completeness summary saved to {yearly_file}")
    
    # Create summary by Cosit
    cosit_summary = results_df.groupby('Cosit').agg({
        'Days_With_Any_Data': 'sum',
        'Days_With_Complete_Data': 'sum',
        'Days_With_Incomplete_Data': 'sum',
        'Days_With_No_Data': 'sum'
    })
    
    # Calculate total possible days across all years for each Cosit
    cosit_total_days = {}
    for cosit in cosits:
        cosit_years = results_df[results_df['Cosit'] == cosit]['Year'].unique()
        total_days = sum(results_df[(results_df['Cosit'] == cosit) & (results_df['Year'] == year)]['Total_Days_In_Year'].iloc[0] for year in cosit_years)
        cosit_total_days[cosit] = total_days
    
    cosit_summary['Total_Possible_Days'] = cosit_summary.index.map(cosit_total_days)
    cosit_summary['Percent_Days_Recorded'] = (cosit_summary['Days_With_Any_Data'] / cosit_summary['Total_Possible_Days']) * 100
    cosit_summary['Percent_Complete_Days'] = (cosit_summary['Days_With_Complete_Data'] / cosit_summary['Total_Possible_Days']) * 100
    
    # Save Cosit summary
    cosit_file = os.path.join(output_dir, f"cosit_completeness_summary_{timestamp}.csv")
    cosit_summary.to_csv(cosit_file)
    print(f"Cosit completeness summary saved to {cosit_file}")
    
    # Print overall statistics
    total_possible_days = results_df['Total_Days_In_Year'].sum()
    total_days_with_any_data = results_df['Days_With_Any_Data'].sum()
    total_days_with_complete_data = results_df['Days_With_Complete_Data'].sum()
    
    print("\nOverall Completeness Statistics:")
    print(f"Total possible days across all Cosits and years: {total_possible_days:,}")
    print(f"Days with any data: {total_days_with_any_data:,} ({total_days_with_any_data/total_possible_days*100:.2f}%)")
    print(f"Days with complete 24-hour data: {total_days_with_complete_data:,} ({total_days_with_complete_data/total_possible_days*100:.2f}%)")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts_processed_20250303_162007.csv")
    
    # Output directory for reports
    output_dir = os.path.join(data_cleaning_dir, "data-quality-reports")
    
    analyze_recording_completeness(input_file, output_dir)