# About This Repo
This repository contains a Python script that helps you extract balanced samples from a dataset based on two key columns: Class and Order. It interactively guides you through choosing a class, how many samples to take, and how many "non-class" orders to include. The result is a new .tsv file containing your sampled data.

The script is called 'subsampling.py'

# Who Can Use This Script?
This script was initially developed for the Knight Lab at UC San Diego, but anyone can use it so long as they have a .tsv data file containing Class and Order columns. Other file formats should also work so long as they are tab delimited.

# Before Running
To make sure you can run this script, please run 'pip install -r requirements.txt'. 

Alternatively: 'pip install pandas numpy'

The script assumes you have python installed on your machine. 

# How to Run
Make sure you are in the data_sampling folder and that you have .tsv file with a 'Class' and 'Order' column. 

Then run the command:
    python subsampling.py --tsv_file path/to/your_data.tsv

The script will prompt you to:
- Select a class to sample from
- Choose how many samples to take
- Specify how many class "orders" to include
- Specify how many non-class "orders" to include
- Name the output file

Your sampled data will be saved as a new .tsv file.

# Developer Notes
- Core function: run_data_sampler(tsv_file)
- Command-line interface is wrapped in main() with argparse
- All sampling is handled using pandas and numpy
