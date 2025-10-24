from typing import Any

def normalize_transaction(t: Any) -> tuple:
    """Converts a transaction object or dict into a standardized, comparable tuple."""
    if isinstance(t, dict):
        category_name = t.get("category", {}).get("name")
        return t.get("amount"), t.get("description"), category_name
    else:
        return t.amount, t.description, t.is_superfluous, t.category.name

def evaluate_correctness(actual: Any, expected: Any, test_type: str) -> float:
    """Returns a score of 1.0 or 0.0."""
    if actual is None and not expected:
        return 1.0
    if actual is None or expected is None:
        return 0.0

    try:
        if test_type == "get":
            if len(actual) != len(expected):
                return 0.0
            actual_set = {normalize_transaction(t) for t in actual}
            expected_set = {normalize_transaction(t) for t in expected}
            return 1.0 if actual_set == expected_set else 0.0
        elif test_type == "insert":
            norm_actual = normalize_transaction(actual)
            norm_expected = normalize_transaction(expected)
            return 1.0 if norm_actual == norm_expected else 0.0
    except Exception:
        return 0.0
    return 0.0