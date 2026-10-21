import pytest

from test_types_demo import calculate_total


@pytest.mark.performance
def test_calculate_total_performance(benchmark):
    # Mede uma carga representativa de 1.000 itens; pytest-benchmark publica as estatisticas.
    items = [(f"item-{index}", index % 5 + 1, 3.25) for index in range(1_000)]
    result = benchmark(calculate_total, items)
    assert result > 0