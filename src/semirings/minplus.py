"""
Min-Plus Semiring Implementation

R_min,+ = (ℝ ∪ {-∞, ∞}, min, +, ∞, 0)

This is a complete idempotent semifield where:
- Addition (⊕) is min
- Multiplication (⊗) is regular addition (+)
- Zero (ε) is ∞
- One (e) is 0
- Inverse of a is -a (negation)

Used for shortest path problems (tropical semiring).
"""

import numpy as np
from .base import IdempotentSemiring


class MinPlusSemiring(IdempotentSemiring):
    """Min-Plus (Tropical) semiring for continuous-valued FCA."""

    @property
    def zero(self) -> float:
        """Additive identity: ∞."""
        return float('inf')

    @property
    def one(self) -> float:
        """Multiplicative identity: 0."""
        return 0.0

    def add(self, a: float, b: float) -> float:
        """Addition: min(a, b)."""
        return min(float(a), float(b))

    def multiply(self, a: float, b: float) -> float:
        """
        Multiplication: a + b (regular addition).
        Special case: ∞ + (-∞) = ∞ (absorbing)
        """
        a, b = float(a), float(b)
        if a == float('inf') or b == float('inf'):
            return float('inf')
        if np.isposinf(a) and np.isneginf(b):
            return float('inf')
        if np.isneginf(a) and np.isposinf(b):
            return float('inf')
        return a + b

    def leq(self, a: float, b: float) -> bool:
        """Natural order: a ≤ b ⟺ min(a, b) = a."""
        return float(a) <= float(b)

    def inverse(self, a: float) -> float:
        """
        Multiplicative inverse: -a (negation).
        For a ≠ ε, a ⊗ (-a) = a + (-a) = 0 = e.
        """
        if a == float('inf'):
            raise ValueError("Cannot invert ∞")
        return -float(a)

    def left_residual(self, a: float, c: float) -> float:
        """
        Left residual: a\\c = c - a
        Finds λ such that a + λ ≥ c (note: order reversed for min).
        """
        a, c = float(a), float(c)
        if a == float('inf'):
            return float('-inf')
        if c == float('inf'):
            return float('inf')
        return c - a

    def right_residual(self, c: float, b: float) -> float:
        """
        Right residual: c/b = c - b
        (Commutative for Min-Plus since addition is commutative)
        """
        return self.left_residual(b, c)

    def __repr__(self):
        return "MinPlusSemiring(ℝ∪{-∞,∞}, min, +, ∞, 0)"
