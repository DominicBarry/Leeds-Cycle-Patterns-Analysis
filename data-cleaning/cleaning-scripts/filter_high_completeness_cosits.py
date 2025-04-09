import os
import pandas as pd
from datetime import datetime

def filter_data_by_cosits_and_date(input_file, output_dir, cosits, start_year=2018, end_year=2023):
    """
    Filters the dataset to include only specified Cosits within a date range
    
    Args:
        input_file (str): Path to the CSV file to process
        output_dir (str): Directory where the filtered file will be saved
        cosits (list): List of Cosit values to include
        start_year (int): Start year for filtering (inclusive)
        end_year (int): End year for filtering (inclusive)
    """
    print(f"Filtering data for {len(cosits)} selected Cosits from {start_year} to {end_year}...")
    
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
    
    # Check if required columns exist
    if 'Sdate' not in df.columns:
        print("Error: Sdate column not found in the CSV file.")
        return
    if 'Cosit' not in df.columns:
        print("Error: Cosit column not found in the CSV file.")
        return
    
    # Extract year from Sdate
    print("Extracting year from Sdate...")
    df['Year'] = pd.to_datetime(df['Sdate'], format='%d/%m/%Y %H:%M', errors='coerce').dt.year
    
    # Count original records by Cosit and Year
    original_counts = df.groupby(['Cosit', 'Year']).size().reset_index(name='Count')
    print(f"Original data has records for {original_counts['Cosit'].nunique()} unique Cosits across {original_counts['Year'].nunique()} years.")
    
    # Filter by Cosit and year
    print("Filtering data...")
    filtered_df = df[(df['Cosit'].isin(cosits)) & (df['Year'] >= start_year) & (df['Year'] <= end_year)]
    
    # Check if we have data after filtering
    if len(filtered_df) == 0:
        print("No data found for the specified Cosits and year range.")
        return
    
    # Count filtered records by Cosit and Year
    filtered_counts = filtered_df.groupby(['Cosit', 'Year']).size().reset_index(name='Count')
    
    # Create a pivot table to show record counts by Cosit and Year
    pivot_counts = filtered_counts.pivot(index='Cosit', columns='Year', values='Count')
    
    # Add totals by Cosit and Year
    pivot_counts['Total'] = pivot_counts.sum(axis=1)
    pivot_counts.loc['Total'] = pivot_counts.sum()
    
    # Save counts summary
    counts_file = os.path.join(output_dir, f"filtered_counts_summary_{timestamp}.csv")
    pivot_counts.to_csv(counts_file)
    print(f"Filtered counts summary saved to {counts_file}")
    
    # Remove the temporary Year column for the final dataset
    filtered_df = filtered_df.drop(columns=['Year'])
    
    # Save the filtered dataframe to a new CSV file
    output_file = os.path.join(output_dir, f"leeds_cycle_counts_filtered_{timestamp}.csv")
    filtered_df.to_csv(output_file, index=False)
    
    print(f"\nFiltering summary:")
    print(f"Original dataset: {len(df):,} rows")
    print(f"Filtered dataset: {len(filtered_df):,} rows ({len(filtered_df)/len(df)*100:.2f}% of original)")
    print(f"Cosits included: {filtered_df['Cosit'].nunique()} out of {len(cosits)} requested")
    print(f"Years included: {filtered_counts['Year'].nunique()} (from {start_year} to {end_year})")
    print(f"\nFiltered dataset saved to {output_file}")

if __name__ == "__main__":
    # Define paths based on your project structure
    current_dir = os.path.dirname(os.path.abspath(__file__))  # cleaning-scripts folder
    data_cleaning_dir = os.path.dirname(current_dir)  # data-cleaning folder
    
    # Input file path
    input_file = os.path.join(data_cleaning_dir, "cleaned-data", "leeds_cycle_counts_processed_20250227_125618.csv")
    
    # Output directory for filtered file
    output_dir = os.path.join(data_cleaning_dir, "cleaned-data")
    
    # Specific Cosits to include
    cosits_to_include = [
        100635, 100636, 100218, 100219, 80474, 
        80475, 90814, 100123, 100633, 100634, 
        90320, 90811
    ]
    
    # Filter the data
    filter_data_by_cosits_and_date(input_file, output_dir, cosits_to_include, 2018, 2023)