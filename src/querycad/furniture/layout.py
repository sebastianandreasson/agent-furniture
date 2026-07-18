"""Small, well-defined layout calculations shared by furniture families."""

from __future__ import annotations


def linear_centers(span: float, item_width: float, count: int) -> tuple[float, ...]:
    """Return evenly spaced item centres across a centred usable span."""

    if count < 1:
        raise ValueError("linear layout count must be at least one")
    if span <= 0 or item_width <= 0:
        raise ValueError("linear layout span and item width must be positive")
    if item_width * count > span:
        raise ValueError("linear layout items do not fit within the span")
    if count == 1:
        return (0.0,)
    pitch = (span - item_width) / (count - 1)
    first = -span / 2 + item_width / 2
    return tuple(first + index * pitch for index in range(count))
