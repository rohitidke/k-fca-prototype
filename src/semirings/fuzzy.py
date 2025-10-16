"""
Fuzzy Semiring (Gödel Semiring) Implementation

G = ([0,1], max, min, 0, 1)

This is the standard fuzzy logic semiring where:
- Addition (⊕) is max (fuzzy OR)
- Multiplication (⊗) is min (fuzzy AND)
- Zero (ε) is 0
- One (e) is 1

Used for fuzzy formal concept analysis and handling degrees of membership.
"""

import numpy as np
from .base import IdempotentSemiring


class FuzzySemiring(IdempotentSemiring):
    """Fuzzy (Gödel) semiring for continuous-valued FCA on [0,1]."""

    @property
    def zero(self) -> float:
        """Additive identity: 0."""
        return 0.0

    @property
    def one(self) -> float:
        """Multiplicative identity: 1."""
        return 1.0

    def add(self, a: float, b: float) -> float:
        """
        Addition: max(a, b).
        Fuzzy OR operation.
        """
        return max(float(a), float(b))

    def multiply(self, a: float, b: float) -> float:
        """
        Multiplication: min(a, b).
        Fuzzy AND operation.
        """
        return min(float(a), float(b))

    def leq(self, a: float, b: float) -> bool:
        """Natural order: a ≤ b in [0,1]."""
        return float(a) <= float(b)

    def left_residual(self, a: float, b: float) -> float:
        """
        Left residual: a \\ b
        Returns the largest x such that a ⊗ x ≤ b
        For Gödel: a \\ b = 1 if a ≤ b, else b
        """
        a, b = float(a), float(b)
        if a <= b:
            return 1.0
        return b

    def right_residual(self, a: float, b: float) -> float:
        """
        Right residual: b / a
        Returns the largest x such that x ⊗ a ≤ b
        For Gödel: b / a = 1 if a ≤ b, else b
        (same as left residual due to commutativity of min)
        """
        return self.left_residual(a, b)

    def __str__(self) -> str:
        """String representation."""
        return "FuzzySemiring([0,1], max, min, 0, 1)"

    def __repr__(self) -> str:
        """String representation."""
        return "FuzzySemiring([0,1], max, min, 0, 1)"
