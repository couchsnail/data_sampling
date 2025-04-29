import pandas as pd
import pytest
from subsampling import get_user_input, get_user_selected_class, filter_data, sample_from_orders, sample_data, run_data_sampler, write_output
from unittest.mock import patch, MagicMock

# Sample dataframe for tests
TEST_DATA = pd.DataFrame({
    'Class': ['Mammal', 'Mammal', 'Bird', 'Bird', 'Reptile', 'Reptile'],
    'Order': ['Carnivora', 'Primates', 'Passeriformes', 'Raptors', 'Squamata', 'Testudines']
})

# Testing handling user input
def test_get_user_input_invalid(monkeypatch):
    inputs = iter(['-1', 'abc', '5'])  # Invalid inputs followed by a valid one
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    result = get_user_input("Enter a positive integer: ", int, lambda x: x > 0, "Invalid input.")
    assert result == 5

# Testing getting the user selected class
def test_get_user_selected_class(monkeypatch):
    # Mocking the input function to return a valid class
    monkeypatch.setattr('builtins.input', lambda _: 'Mammal')
    selected_class = get_user_selected_class(TEST_DATA)
    assert selected_class == 'Mammal'

def test_get_user_selected_class_multiple_invalid(monkeypatch):
    inputs = iter(['InvalidClass', 'AnotherInvalid', 'Mammal'])
    
    def fake_input(prompt):
        try:
            return next(inputs)
        except StopIteration:
            raise Exception("Test input exhausted; get_user_selected_class() did not accept a valid value.")

    monkeypatch.setattr('builtins.input', fake_input)
    
    selected_class = get_user_selected_class(TEST_DATA)
    assert selected_class == 'Mammal'

# Testing the data filtering function
def test_filter_data_positive_1():
    result = filter_data(TEST_DATA, 'Class', 'Mammal')
    assert len(result) == 2
    assert all(result['Class'] == 'Mammal')

def test_filter_data_positive_2():
    result = filter_data(TEST_DATA, 'Class', 'Reptile')
    assert len(result) == 2
    assert all(result['Class'] == 'Reptile')

def test_filter_data_column_error():
    with pytest.raises(ValueError):
        filter_data(TEST_DATA, 'NonExistentColumn', 'Mammal')

def test_filter_data_negative_1():
    result = filter_data(TEST_DATA, 'Class', 'Mammal', negate=True)
    assert all(result['Class'] != 'Mammal')

def test_filter_data_negative_2():
    result = filter_data(TEST_DATA, 'Class', 'Reptile', negate=True)
    assert all(result['Class'] != 'Reptile')

def test_filter_data_empty():
    result = filter_data(TEST_DATA, 'Class', 'Fish')
    assert len(result) == 0

# Testing the sampling function
def test_sample_from_orders_empty():
    orders = ['Carnivora', 'Primates']
    sampled = sample_from_orders(TEST_DATA, orders, 0)
    assert len(sampled) == 0

def test_sample_from_orders():
    orders = ['Carnivora', 'Primates']
    sampled = sample_from_orders(TEST_DATA, orders, 2)
    assert len(sampled) == 2
    assert all(sampled['Order'].isin(orders))

# It will obtain 5 samples, despite there being only 1 sample in the given order
# This is expected behvavior, as the code modification that fixes this is in the run_data_sampler function
def test_sample_from_orders_not_enough():
    orders = ['Carnivora']
    sampled = sample_from_orders(TEST_DATA, orders, 5)
    assert len(sampled) == 5
    assert all(sampled['Order'] == 'Carnivora')

# Testing the main sampling function
def test_sample_data_combination_1():
    result = sample_data(TEST_DATA, 'Mammal', num_samples=4, num_orders=2, num_norders=2)
    assert len(result) == 8 
    assert 'Class' in result.columns
    assert 'Order' in result.columns

def test_sample_data_combination_2():
    result = sample_data(TEST_DATA, 'Bird', num_samples=10, num_orders=2, num_norders=2)
    assert len(result) == 20
    assert 'Class' in result.columns
    assert 'Order' in result.columns

def test_sample_data_no_class():
    with pytest.raises(ValueError):
        sample_data(TEST_DATA, 'Fish', num_samples=4, num_orders=2, num_norders=2)

def test_sample_data_unequal_order():
    result = sample_data(TEST_DATA, 'Bird', num_samples=10, num_orders=1, num_norders=2)
    assert len(result) == 20
    assert 'Class' in result.columns
    assert 'Order' in result.columns

def test_sample_data_not_enough_orders_select():
    with pytest.raises(ValueError):
        sample_data(TEST_DATA, 'Mammal', num_samples=4, num_orders=5, num_norders=2)

def test_sample_data_not_enough_orders_nonselect():
    with pytest.raises(ValueError):
        sample_data(TEST_DATA, 'Mammal', num_samples=4, num_orders=2, num_norders=10)

# Testing the run_data_sampler function
@patch("subsampling.get_user_input")
@patch("subsampling.get_user_selected_class")
@patch("subsampling.write_output")
def test_run_data_sampler(mock_write_output, mock_get_user_selected_class, mock_get_user_input, tmp_path):
    # Mock user inputs
    mock_get_user_selected_class.return_value = 'Mammal'
    mock_get_user_input.side_effect = [
        2,  # num_samples
        1,  # num_orders
        1,  # num_norders
        "output_file.tsv"  # output file name
    ]

    # Create a temporary file for testing
    temp_file = tmp_path / "test_data.tsv"
    TEST_DATA.to_csv(temp_file, sep='\t', index=False)

    # Mock write_output to avoid actual file writing
    mock_write_output.return_value = None

    # Run the function
    run_data_sampler(temp_file)

    # Assertions
    mock_get_user_selected_class.assert_called_once()
    assert mock_get_user_input.call_count == 4
    mock_write_output.assert_called_once()


@patch("subsampling.get_user_input")
@patch("subsampling.get_user_selected_class")
@patch("subsampling.write_output")
def test_run_data_sampler_insufficient_samples(mock_write_output, mock_get_user_selected_class, mock_get_user_input, tmp_path):
    # Mock user inputs
    mock_get_user_selected_class.return_value = 'Mammal'
    mock_get_user_input.side_effect = [
        10,  # num_samples (more than available)
        1,   # num_orders
        1,   # num_norders
        "output_file.tsv"  # output file name
    ]

    # Create a temporary file for testing
    temp_file = tmp_path / "test_data.tsv"
    TEST_DATA.to_csv(temp_file, sep='\t', index=False)

    # Mock write_output to avoid actual file writing
    mock_write_output.return_value = None

    # Run the function
    run_data_sampler(temp_file)

    # Assertions
    mock_get_user_selected_class.assert_called_once()
    assert mock_get_user_input.call_count == 4
    mock_write_output.assert_called_once()

@patch("subsampling.get_user_input")
@patch("subsampling.get_user_selected_class")
def test_run_data_sampler_invalid_class(mock_get_user_selected_class, mock_get_user_input, tmp_path):
    # Mock user inputs
    mock_get_user_selected_class.side_effect = ValueError("Invalid class selected.")
    mock_get_user_input.return_value = None

    # Create a temporary file for testing
    temp_file = tmp_path / "test_data.tsv"
    TEST_DATA.to_csv(temp_file, sep='\t', index=False)

    # Run the function and expect it to handle the error
    with pytest.raises(ValueError, match="Invalid class selected."):
        run_data_sampler(temp_file)

    mock_get_user_selected_class.assert_called_once()
    mock_get_user_input.assert_not_called()