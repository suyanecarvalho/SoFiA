from typing import Any

def normalize_transaction(t: Any) -> tuple:
    """Converts a transaction object or dict into a standardized, comparable tuple."""
    if isinstance(t, dict):
        category = t.get("category", {}) or {}
        category_name = category.get("name")
        return (
            t.get("amount"),
            t.get("description"),
            t.get("is_superfluous", False),
            category_name
        )
    else:
        return (
            t.amount,
            t.description,
            t.is_superfluous,
            t.category.name
        )


def calculate_score(actual: Any, expected: Any, test_type: str, difficulty: str) -> int:
    """
    Calculates the score for a test case based on correctness and difficulty.
    - easy: 1 point
    - medium: 2 points
    - hard: 4 points
    - incorrect: 0 points
    """
    score_map = {
        "easy": 1,
        "medium": 2,
        "hard": 4,
    }
    points = score_map.get(difficulty, 1)
    if actual is None and not expected:
        return points
    if actual is None or expected is None:
        return 0
    is_correct = False
    try:
        if test_type in ["get", "insert"]:
            if len(actual) != len(expected):
                is_correct = False
            else:
                actual_set = {normalize_transaction(t) for t in actual}
                expected_set = {normalize_transaction(t) for t in expected}
                is_correct = actual_set == expected_set

    except Exception:
        is_correct = False

    return points if is_correct else 0