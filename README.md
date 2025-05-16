# About This Repo
This repository contains a Python script that helps you extract balanced samples from a dataset based on two key columns of your choosing. It interactively guides you through choosing a main grouping column, how many samples to take, and how many "non-main-group" orders to include. The result is a new .tsv file containing your sampled data.

The script is called 'subsampling.py'

# Who Can Use This Script?
This script was initially developed for the Knight Lab at UC San Diego, but anyone can use it so long as they have a dataset in the .tsv, .csv, or .txt file formats (provided the .txt file is tab-delimited) containing at least two categorical columns (e.g. 'Class' and 'Order').  

# Before Running
To make sure you can run this script, please run 'pip install -r requirements.txt'. 

Alternatively: 'pip install pandas numpy'

The script assumes you have python installed on your machine. 

# How to Run
Make sure you are in the data_sampling folder and that you have .tsv, .csv, or .txt file with at least 2 columns. 

Then run the command:
    python subsampling.py --tsv_file path/to/your_data.tsv

The script will prompt you to:
- Select a main grouping column (e.g., 'Class')
- Select a value from that column to sample from (e.g., 'Amphibia')
- Select a secondary grouping column (e.g., 'Order')
- Enter:
    - Number of samples to take from the selected group
    - Number of unique secondary values (e.g., 'Order') to sample within the selected group
    - Number of unique secondary values to sample from the non-selected group
- Enter a name for the output file

Your sampled data will be saved as a new .tsv file.

# Example Use Case
Say you have a dataset on microbiome samples from many different animals. Columns include 'Phylum', 'Class', and 'Order'. 

Your objective:
- Sample 10 values from the 'Amphibia' class across 3 orders
- For comparison, sample 10 values that are not of the 'Amphibia' class across 3 orders 

The script would guide you to:
- Select a class to sample from
- Choose how many samples to take
- Specify how many class "orders" to include
- Specify how many non-class "orders" to include
- Name the output file

The script would then output a .tsv_file with 20 values, 10 of which have 'Class' of Amphibia and 10 of which do not. You can see the results under the 'sample_output' folder in this repository. 

# Developer Notes
- Core function: run_data_sampler(tsv_file)
- Command-line interface is wrapped in main() with argparse
- All sampling is handled using pandas and numpy
