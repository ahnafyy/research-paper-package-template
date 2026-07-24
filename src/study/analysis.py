from __future__ import annotations

from fractions import Fraction
from typing import Any


def expected_distinct_choices(options: int, choices: int) -> Fraction:
    """Return the exact expected occupied-option count for uniform independent choices."""
    if options <= 0 or choices < 0:
        raise ValueError("options must be positive and choices must be non-negative")
    return options * (1 - Fraction(options - 1, options) ** choices)


def run_analysis(seed: int) -> dict[str, Any]:
    """Run the checked template fixture; replace this body for a real study."""
    options = 8
    choices = 4
    expected = expected_distinct_choices(options, choices)
    return {
        "choices": choices,
        "expected_distinct": float(expected),
        "expected_distinct_denominator": expected.denominator,
        "expected_distinct_numerator": expected.numerator,
        "options": options,
        "random_seed": seed,
    }
