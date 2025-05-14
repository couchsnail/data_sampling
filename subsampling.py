import argparse
import pandas as pd
import numpy as np
from itertools import cycle

def parse_args():
    parser = argparse.ArgumentParser(description="Script for extracting data from a data file")
    parser.add_argument("--tsv_file", type=str, required=True, help="Enter the path to the data file")
    return parser.parse_args()

def load_data(file_path):
    file_path_str = str(file_path)
    try:
        # Trying to detect the file type based on the extension
        if file_path_str.endswith('.tsv') or file_path_str.endswith('.txt'):
            data = pd.read_csv(file_path_str, sep='\t')
        else:
            data = pd.read_csv(file_path_str)
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to load data: {e}")

def get_user_input(prompt, input_type=int, condition=lambda x: True, error_msg="Invalid input"):
    while True:
        try:
            print("Press 'quit' or 'cancel' to exit.")
            user_input = input(prompt)
            if user_input.lower() in ["quit", "cancel"]:
                print("Operation canceled by the user.")
                return None 
            value = input_type(user_input)
            if not condition(value):
                raise ValueError
            return value
        except ValueError:
            print(error_msg)

def get_user_selected_column(data, prompt="Select a column: "):
    existing_columns = data.columns.tolist()
    while True:
        print("Press 'quit' or 'cancel' to exit.")
        selected_column = input(f"{prompt} (options: {existing_columns}, or type 'quit' to cancel): ")
        if selected_column.lower() in ["quit", "cancel"]:
            print("Operation canceled by the user.")
            return None  
        if selected_column in existing_columns:
            return selected_column
        else:
            print("Invalid column selected. Please choose from the available columns.")

def get_user_selected_value_from_selected_column(data, selected_column):
    existing_values = data[selected_column].dropna().unique()
    while True:
        print("Press 'quit' or 'cancel' to exit.")
        selected_value = input(f"Enter a {selected_column} to select (options: {existing_values}, or type 'quit' to cancel): ")
        if selected_value.lower() in ["quit", "cancel"]:
            print("Operation canceled by the user.")
            return None  
        if selected_value in existing_values:
            return selected_value
        else:
            print("Invalid value selected. Please choose from the available values within this column.")

def filter_data(data, column, value, negate=False):
    if column not in data.columns:
        raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
    if negate:
        return data[data[column] != value]
    else:
        return data[data[column] == value]

def sample_from_column(data_subset, organization_column, orders_to_sample_from, total_samples):
    if total_samples > len(data_subset[data_subset[organization_column].isin(orders_to_sample_from)]):
        raise ValueError(
            f"Not enough data to sample {total_samples} items from the given {organization_column}."
        )
    
    sampled = pd.DataFrame()
    order_cycle = cycle(orders_to_sample_from)
    while len(sampled) < total_samples:
        current_order = next(order_cycle)
        subset = data_subset[data_subset[organization_column] == current_order]
        if not subset.empty:
            sampled = pd.concat([sampled, subset.sample(n=1, replace=True)], ignore_index=True)
    return sampled

def sample_data(data, selected_value, selected_column, organization_column, num_samples, num_orders, num_norders):
    selected_subset = filter_data(data, selected_column, selected_value)
    if selected_subset.empty:
        raise ValueError(f"No data matching {selected_value} in {selected_column} found.")

    unique_orders = selected_subset[organization_column].dropna().unique()
    chosen_orders = np.random.choice(unique_orders, num_orders, replace=False)
    print(f"Selected orders from class '{selected_value}': {chosen_orders}")

    selected_samples = sample_from_column(selected_subset, organization_column, chosen_orders, num_samples)

    nonselected_subset = filter_data(data, selected_column, selected_value, negate=True)
    valid_norders = nonselected_subset[organization_column].dropna().unique()
    if num_norders > len(valid_norders):
        raise ValueError(f"Not enough unique data matching values that are not {selected_value} to sample from.")

    chosen_norders = np.random.choice(valid_norders, num_norders, replace=False)
    print(f"Selected orders from non-selected class: {chosen_norders}")

    nonselected_samples = sample_from_column(nonselected_subset, organization_column, chosen_norders, num_samples)

    return pd.concat([selected_samples, nonselected_samples], ignore_index=True)

def run_data_sampler(tsv_file):
    data = load_data(tsv_file)
    print(f"Columns in data: {data.columns.tolist()}")

    # Prompts user for the main grouping column (e.g., Class)
    selected_column = get_user_selected_column(data, "Enter the main grouping column")
    if selected_column is None:
        return

    # Prompts user for the value to sample from the selected column (ex: 'Amphibia')
    selected_value = get_user_selected_value_from_selected_column(data, selected_column)
    if selected_value is None:
        return

    # Prompts user for an organization column (e.g., Order)
    organization_column = get_user_selected_column(data, "Enter the secondary column to organize sampling from")
    if organization_column is None:
        return

    # Prompts user for the number of samples to select from each group
    print(f"Number of samples available matching selected value: {len(data[data[selected_column] == selected_value])}")
    num_samples = get_user_input("Enter the number of samples to select from each group: ", int, lambda x: x > 0)
    if num_samples > len(data[data[selected_column] == selected_value]):
        print(f"Not enough data to sample {num_samples} items from the given {selected_column}.")
        num_samples = len(data[data[selected_column] == selected_value])
    
    # Prompts user for the number of unique values to sample from
    # the selected value and the number of unique values to sample from the non-selected group
    print(f"Number of unique '{organization_column}' values available matching selected value: {len(data[data[selected_column] == selected_value][organization_column].dropna().unique())}")
    num_orders = get_user_input(f"Enter the number of unique '{organization_column}' values to sample from {selected_value}: ", int, lambda x: x > 0)
    if num_orders > len(data[data[selected_column] == selected_value][organization_column].dropna().unique()):
        print(f"Not enough unique data to sample {num_orders} items from the given {organization_column}.")
        num_orders = len(data[data[selected_column] == selected_value][organization_column].dropna().unique())
    print(f"Number of unique '{organization_column}' values available matching non-selected value: {len(data[data[selected_column] != selected_value][organization_column].dropna().unique())}")
    num_norders = get_user_input(f"Enter the number of unique '{organization_column}' values to sample from non-{selected_value} group: ", int, lambda x: x > 0)
    if num_norders > len(data[data[selected_column] != selected_value][organization_column].dropna().unique()):
        print(f"Not enough unique data to sample {num_norders} items from the given {organization_column}.")
        num_norders = len(data[data[selected_column] != selected_value][organization_column].dropna().unique())

    try:
        result = sample_data(data, selected_value, selected_column, organization_column, num_samples, num_orders, num_norders)
        print(result)
    except Exception as e:
        print(f"Error during sampling: {e}")
        return

    output_file = input("Enter output filename (default: sampled_data.tsv): ").strip() or "sampled_data.tsv"
    write_output(result, output_file if output_file.endswith(".tsv") else output_file + ".tsv")

def write_output(data, output_file):
    try:
        data.to_csv(output_file, sep='\t', index=False)
        print(f"Output written to {output_file}")
    except Exception as e:
        raise RuntimeError(f"Failed to write output: {e}")

def main():
    args = parse_args()
    run_data_sampler(args.tsv_file)

if __name__ == "__main__":
    main()