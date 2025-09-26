from typing import Any


T = Any
L = Any

def clamp(min_val: T, val: T, mav_val: T) -> T:
    """Clamp a `val` to be no lower than `minVal`, and no higher than `maxVal`."""
    return max(min_val, min(mav_val, val))

def snap(n: float, increments: int) -> float:
    return round(increments * n) / increments

def map_range(x: L, n1: L, m1: L, n2: L = -1, m2: L = 1) -> L:
    """Scale a value `x` that is currently somewhere between `n1` and `m1` to now be in an
    equivalent position between `n2` and `m2`."""
    # Make the range start at 0.
    old_max = m1 - n1
    old_x = x - n1
    percentage = old_x / old_max

    # Shmoove it over.
    new_max = m2 - n2
    new_pos = new_max * percentage
    ans = new_pos + n2
    return ans
