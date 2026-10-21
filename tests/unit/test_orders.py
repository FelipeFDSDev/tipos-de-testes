import pytest

from test_types_demo import calculate_total


@pytest.mark.unit
def test_calculate_total_for_multiple_items():
    assert calculate_total([("Livro", 2, 19.90), ("Caneta", 3, 2.00)]) == 45.8


@pytest.mark.unit
@pytest.mark.parametrize("items", [[], [("", 1, 2)], [("Item", 0, 2)], [("Item", 1, -1)]])
def test_calculate_total_rejects_invalid_items(items):
    with pytest.raises(ValueError):
        calculate_total(items)
