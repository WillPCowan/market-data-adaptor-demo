import decimal
import pytest
import demo.connectivity.common.json as json

def _make_dumps_test_cases():
    return [
        (
            {"decimal": decimal.Decimal("3.14159")},
            '{"decimal": 3.14159}'
        ),
        (
            {"key": "value"},
            '{"key": "value"}'
        ),
        (
            {"nested": {"key": "value"}},
            '{"nested": {"key": "value"}}'
        ),
        (
            {"list": [1, 2, 3]},
            '{"list": [1, 2, 3]}'
        )
    ]

def _make_loads_test_cases():
    return [
        (
            '{"decimal": 3.14159}',
            {"decimal": decimal.Decimal("3.14159")}
        ),
        (
            '{"key": "value"}',
            {"key": "value"}
        ),
        (
            '{"nested": {"key": "value"}}',
            {"nested": {"key": "value"}}
        ),
        (
            '{"list": [1, 2, 3]}',
            {"list": [1, 2, 3]}
        )
    ]

@pytest.mark.parametrize("input_obj,expected_output", _make_dumps_test_cases())
def test_dumps(input_obj, expected_output):
    assert json.dumps(input_obj) == expected_output

@pytest.mark.parametrize("input_str,expected_output", _make_loads_test_cases())
def test_loads(input_str, expected_output):
    assert json.loads(input_str) == expected_output