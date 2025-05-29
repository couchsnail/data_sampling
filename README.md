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
    python subsampling.py --tsv_file 'path/to/your_data.tsv'

Make sure to put your file path in quotes. 

The script will prompt you to:
- Select a main grouping column (e.g., 'Class')
- Select a value from that column to sample from (e.g., 'Amphibia')
- Select a secondary grouping column (e.g., 'Order')
- Enter:
    - Number of samples to take from the selected group
    - Number of subgroups (e.g., 'Order') to sample within the selected group
    - (Optional) Number of unique subgroups to sample from the non-selected group
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

# Saying "No" to Sampling the Non-Selected Group
Let’s say you’re working with a dataset of animal microbiome samples and your table includes columns like Class and Order. You choose:
- Main column: Class
- Value to sample from: Amphibia
- Secondary column: Order
- Number of Amphibia orders: 3
- When asked about sampling from non-Amphibia (i.e., all other classes), you say “No”

## What the Script Will Do:
Instead of asking how many non-Amphibia Orders to include, the script will simply:
- Grab all the rows that are not Amphibia
- Skip any sampling or filtering by Order for this non-selected group

This behavior will also occur if there are not enough groups in the non-selected group.

# Edge Cases
## 1. Choosing too many samples
If you ask for more samples than actually exist in a group (e.g. 50 samples from the Class 'Amphibia', but only 30 exist), the script will:
1) Tell you there aren't enough items
2) Take all available samples instead without stopping

## 2. You ask for more groups than exist
Let’s say you want samples from 5 unique Orders in Amphibia, but there are only 3. The script will:
1) Warn you about the mismatch
2) Use all available Orders instead of stopping

## 3. You ask for more non-selected orders than exist
Just like with the selected group, if you ask for more Orders than are available in the non-selected group:
1) You’ll get a message
2) The script will use all available non-selected Orders instead

## 4. Your dataset has missing or unexpected values
If any of your chosen columns (like Order) have missing data (NaN values), the script automatically ignores those rows when calculating unique values or sampling groups.

## 5. You enter invalid inputs
If you enter something invalid — like a negative number, a column name that doesn’t exist, or a string when it asked for a number, the script will keep prompting you until you enter something valid.

## 6. You don't provide an output file name
No worries! If you leave the filename blank when prompted, the script will automatically save your data as 'sampled_data.tsv'

# Developer Notes
- Core function: run_data_sampler(tsv_file)
- Command-line interface is wrapped in main() with argparse
- All sampling is handled using pandas and numpy