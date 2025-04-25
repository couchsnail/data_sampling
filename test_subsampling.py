import pandas as pd
import pytest
from subsampling import get_user_selected_class, filter_data, sample_from_orders, sample_data

# Sample dataframe for tests
TEST_DATA = pd.DataFrame({
    'Class': ['Mammal', 'Mammal', 'Bird', 'Bird', 'Reptile', 'Reptile'],
    'Order': ['Carnivora', 'Primates', 'Passeriformes', 'Raptors', 'Squamata', 'Testudines']
})

# Testing getting the user selected class
def test_get_user_selected_class(monkeypatch):
    # Mocking the input function to return a valid class
    monkeypatch.setattr('builtins.input', lambda _: 'Mammal')
    selected_class = get_user_selected_class(TEST_DATA)
    assert selected_class == 'Mammal'

def test_get_user_selected_class_invalid(monkeypatch):
    # Mocking the input function to return an invalid class
    monkeypatch.setattr('builtins.input', lambda _: 'InvalidClass')
    with pytest.raises(ValueError):
        get_user_selected_class(TEST_DATA)

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

def test_filter_data_negative_1():
    result = filter_data(TEST_DATA, 'Class', 'Reptile', negate=True)
    assert all(result['Class'] != 'Reptile')

def test_filter_data_empty():
    result = filter_data(TEST_DATA, 'Class', 'Fish')
    assert len(result) == 0

# # Testing the sampling function
def test_sample_from_orders_empty():
    orders = ['Carnivora', 'Primates']
    sampled = sample_from_orders(TEST_DATA, orders, 0)
    assert len(sampled) == 0

def test_sample_from_orders():
    orders = ['Carnivora', 'Primates']
    sampled = sample_from_orders(TEST_DATA, orders, 5)
    assert len(sampled) == 5
    assert all(sampled['Order'].isin(orders))

# Expected behavior: it will sample the one sample available 5 times
# Need to check if this is in line with expectations
def test_sample_from_orders_not_enough():
    orders = ['Carnivora']
    sampled = sample_from_orders(TEST_DATA, orders, 5)
    assert len(sampled) == 5
    assert all(sampled['Order'] == 'Carnivora')

# Testing the main sampling function
def test_sample_data_combination_1():
    result = sample_data(TEST_DATA, 'Mammal', num_samples=4, num_norders=2)
    assert len(result) == 8 
    assert 'Class' in result.columns
    assert 'Order' in result.columns

def test_sample_data_combination_2():
    result = sample_data(TEST_DATA, 'Bird', num_samples=10, num_norders=2)
    assert len(result) == 20
    assert 'Class' in result.columns
    assert 'Order' in result.columns

def test_sample_data_no_class():
    with pytest.raises(ValueError):
        sample_data(TEST_DATA, 'Fish', num_samples=4, num_norders=2)

def test_sample_data_not_enough_orders():
    with pytest.raises(ValueError):
        sample_data(TEST_DATA, 'Mammal', num_samples=4, num_norders=10)