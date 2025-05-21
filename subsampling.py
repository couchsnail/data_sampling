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
    existing_values = data[selected_column].dropna().unique().tolist()
    if not existing_values:
        print(f"No values found in column '{selected_column}'.")
        return None
    value_type = type(existing_values[0])
    while True:
        print("Press 'quit' or 'cancel' to exit.")
        selected_value = input(f"Enter a {selected_column} to select (options: {existing_values}, or type 'quit' to cancel): ")
        if selected_value.lower() in ["quit", "cancel"]:
            print("Operation canceled by the user.")
            return None
        try:
            # Convert input to the correct type
            typed_value = value_type(selected_value)
            if typed_value in existing_values:
                return typed_value
            else:
                print("Invalid value selected. Please choose from the available values within this column.")
        except ValueError:
            print(f"Invalid type. Please enter a valid {value_type.__name__} value.")

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

def sample_data(data,value,column,organization_column,num_samples,num_orders,negate=False, want_orders=True):
    subset = filter_data(data, column, value, negate=negate)
    if subset.empty:
        raise ValueError(f"No data matching {'not ' if negate else ''}{value} in {column} found.")

    if want_orders:
        unique_groups = subset[organization_column].dropna().unique()
        if num_orders > len(unique_groups):
            raise ValueError(f"Not enough unique values in {organization_column} to sample {num_orders} groups.")

        chosen_groups = np.random.choice(unique_groups, num_orders, replace=False)
        group_label = f"non-{value}" if negate else value
        print(f"Selected orders from {column} '{group_label}': {chosen_groups}")

        return sample_from_column(subset, organization_column, chosen_groups, num_samples)
    else:
        return subset.sample(n=num_samples, replace=True)

# Need to redocument this
# Default: for non-selected values, will just randomly subsample without input number of orders
# Default if you don't sample anything gets the whole table
# If the number of desired orders is greater than the number of available orders, 
# pull entire rest of the table by default
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
        print("Selecting maximum available samples instead.")
        num_samples = len(data[data[selected_column] == selected_value])
    
    # Flag for if the user has enough orders to match desired samples
    enough_orders = True

    # Prompts user for the number of unique values to sample from
    # the selected value and the number of unique values to sample from the non-selected group
    print(f"Number of unique '{organization_column}' values available matching selected value: {len(data[data[selected_column] == selected_value][organization_column].dropna().unique())}")
    num_orders = get_user_input(f"Enter the number of unique '{organization_column}' values to sample from {selected_value}: ", int, lambda x: x > 0)

    if num_orders > len(data[data[selected_column] == selected_value][organization_column].dropna().unique()):
        print(f"Not enough unique data to sample {num_orders} items from the given {organization_column}.")
        print("Selecting maximum available orders instead.")
        num_orders = len(data[data[selected_column] == selected_value][organization_column].dropna().unique())
        enough_orders = False

    # Want to check if user wants to input the number of orders to sample from the non-selected group
    # If not, sample without considering orders
    num_norders = None
    choose_orders = get_user_input(
        "Do you want to input the number of orders to sample from the non-selected group? (y/n): ",
        str,
        lambda x: x.lower() in ['y', 'n']
    )
    if choose_orders is None:
        return

    if choose_orders.lower() == 'y':
        n_unique_norders = len(
            data[data[selected_column] != selected_value][organization_column].dropna().unique()
        )
        print(f"Number of unique '{organization_column}' values available in non-selected group: {n_unique_norders}")
        num_norders = get_user_input(
            f"Enter number of unique '{organization_column}' values to sample from non-{selected_value} group: ",
            int,
            lambda x: x > 0
        )
        if num_norders > n_unique_norders:
            print(f"Only {n_unique_norders} available. Sampling from all.")
            num_norders = n_unique_norders

    try:
        selected_sample = sample_data(
            data, selected_value, selected_column, organization_column,
            num_samples, num_orders,
            want_orders=enough_orders
        )

        if choose_orders.lower() == 'y':
            non_selected_sample = sample_data(
                data, selected_value, selected_column, organization_column,
                num_samples, num_norders,
                negate=True, want_orders=True
            )
        else:
            # Sample total num_samples from all non-selected data (not per order)
            non_selected_sample = sample_data(
                data, selected_value, selected_column, organization_column,
                num_samples, 0,
                negate=True, want_orders=False
            )

        result = pd.concat([selected_sample, non_selected_sample], ignore_index=True)
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