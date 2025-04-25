import argparse
import pandas as pd
import numpy as np
from itertools import cycle

def parse_args():
    parser = argparse.ArgumentParser(description="Script for extracting data from a data file")
    parser.add_argument("--tsv_file", type=str, required=True, help="Enter the path to the data file")
    return parser.parse_args()

def load_data(file_path):
    try:
        data = pd.read_csv(file_path, sep='\t')
        if 'Class' not in data.columns or 'Order' not in data.columns:
            raise KeyError("Dataset must contain 'Class' and 'Order' columns.")
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}")

def get_user_input(prompt, input_type=int, condition=lambda x: True, error_msg="Invalid input"):
    while True:
        try:
            value = input_type(input(prompt))
            if not condition(value):
                raise ValueError
            return value
        except ValueError:
            print(error_msg)

def get_user_selected_class(data):
    existing_classes = data['Class'].unique()
    while True:
        selected_class = input(f"Enter a Class to select (options: {existing_classes}): ")
        if selected_class in existing_classes:
            return selected_class
        else:
            raise ValueError("Invalid class selected. Please choose from the available classes.")

def filter_data(data, column, value, negate=False):
    if column not in data.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    if negate:
        return data[data[column] != value]
    else:
        return data[data[column] == value]

def sample_from_orders(data_subset, orders, total_samples):
    sampled = pd.DataFrame()
    order_cycle = cycle(orders)
    while len(sampled) < total_samples:
        current_order = next(order_cycle)
        subset = data_subset[data_subset['Order'] == current_order]
        if not subset.empty:
            sampled = pd.concat([sampled, subset.sample(n=1, replace=True)], ignore_index=True)
    return sampled

def sample_data(data, selected_class, num_samples, num_norders):
    class_subset = filter_data(data, 'Class', selected_class)
    if class_subset.empty:
        raise ValueError("No data found for the selected class.")

    unique_orders = class_subset['Order'].dropna().unique()
    num_orders_to_sample = min(5, len(unique_orders))
    chosen_orders = np.random.choice(unique_orders, num_orders_to_sample, replace=False)
    print(f"Selected orders from class '{selected_class}': {chosen_orders}")

    selected_samples = sample_from_orders(class_subset, chosen_orders, num_samples)

    nonselected_subset = filter_data(data, 'Class', selected_class, negate=True)
    valid_norders = nonselected_subset['Order'].dropna().unique()
    if num_norders > len(valid_norders):
        raise ValueError("Not enough unique non-selected orders to sample from.")

    chosen_norders = np.random.choice(valid_norders, num_norders, replace=False)
    print(f"Selected orders from non-selected class: {chosen_norders}")

    nonselected_samples = sample_from_orders(nonselected_subset, chosen_norders, num_samples)

    return pd.concat([selected_samples, nonselected_samples], ignore_index=True)

def write_output(data, output_file):
    try:
        data.to_csv(output_file, sep='\t', index=False)
        print(f"Output written to {output_file}")
    except Exception as e:
        raise RuntimeError(f"Failed to write output: {e}")

def run_data_sampler(tsv_file):
    data = load_data(tsv_file)
    print(f"Columns in data: {data.columns.tolist()}")

    selected_class = get_user_selected_class(data)
    num_samples = get_user_input("Enter the number of samples to select: ", int, lambda x: x > 0, "Please enter a positive integer.")
    print(f"Number of orders in selected class '{selected_class}': {len(data[data['Class'] == selected_class]['Order'].dropna().unique())}")
    print(f"Number of orders in non-selected class: {len(data[data['Class'] != selected_class]['Order'].dropna().unique())}")
    num_norders = get_user_input("Enter the number of non-selected orders to sample: ", int, lambda x: x > 0, "Please enter a positive integer.")

    try:
        result = sample_data(data, selected_class, num_samples, num_norders)
        print("Sampled data:")
        print(result)
    except Exception as e:
        print(f"Error during sampling: {e}")

    output_file_name = get_user_input("Enter the output file name (default: sampled_data.tsv): ", str, lambda x: x.strip() != "", "File name cannot be empty.")
    write_output(result, output_file_name if output_file_name.endswith('.tsv') else output_file_name + '.tsv')

def main():
    args = parse_args()
    run_data_sampler(args.tsv_file)

if __name__ == "__main__":
    main()