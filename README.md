# data_sampling
This repository contains a script to sample data from a TSV file according to given parameters into a separate TSV file. 

To make sure you can run this script, please run 'pip install -r requirements.txt'. 

The script assumes you have python installed on your machine. 

Relevant functions:
filter_data(): Given a Pandas DataFrame, filter by a given column.
run_data_sampler(): Loads data in from a tsv file and allows the user to subsample it for bootstrap testing. 