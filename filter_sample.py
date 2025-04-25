import argparse
import pandas as pd
from data_sampling.subsampling import filter_data, write_output

def main():
    parser = argparse.ArgumentParser(description="Data subsampling tool")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: filter_data
    parser_filter = subparsers.add_parser("filter_data", help="Filter the dataset by column/value")
    parser_filter.add_argument("--tsv_file", required=True, help="Path to the TSV data file")
    parser_filter.add_argument("--column", required=True, help="Column to filter on")
    parser_filter.add_argument("--value", required=True, help="Value to filter for")
    parser_filter.add_argument("--negate", action="store_true", help="Negate the filter condition")
    parser_filter.add_argument("--output", help="File to write filtered results")

    args = parser.parse_args()

    if args.command == "filter_data":
        data = pd.read_csv(args.tsv_file, sep='\t')
        filtered = filter_data(data, args.column, args.value, negate=args.negate)
        print(filtered)

        if args.output:
            write_output(filtered, args.output if args.output_file_name.endswith('.tsv') else args.output + '.tsv')
            print(f"Filtered data written to {args.output}")

if __name__ == "__main__":
    main()


