from typing import List


def divide_numbers(a: float, b: float) -> float:
    """Divides a by b, raising a clear error if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def get_average(numbers: List[float]) -> float:
    """Returns the average of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot average an empty list")
    return sum(numbers) / len(numbers)


def add_item(items: List, new_item) -> List:
    """Returns a new list with new_item appended, without mutating the original."""
    return items + [new_item]
