from __future__ import annotations

from typing import Any

from paperkit.claims import Claim, ClaimEvaluation


def evaluate_expected_distinct(results: dict[str, Any], claim: Claim) -> ClaimEvaluation:
    observed = float(results["expected_distinct"])
    expected = 3.310546875
    tolerance = claim.tolerance if claim.tolerance is not None else 0.0
    difference = abs(observed - expected)
    return ClaimEvaluation(
        passed=difference <= tolerance,
        observed=observed,
        expected=expected,
        detail=f"Absolute difference {difference:.3g} <= tolerance {tolerance:.3g}.",
    )
