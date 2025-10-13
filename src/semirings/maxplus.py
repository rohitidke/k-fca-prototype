"""
Max-Plus Semiring Implementation

R_max,+ = (ℝ ∪ {-∞, ∞}, max, +, -∞, 0)

This is a complete idempotent semifield where:
- Addition (⊕) is max
- Multiplication (⊗) is regular addition (+)
- Zero (ε) is -∞
- One (e) is 0
- Inverse of a is -a (negation)

Used for shortest path problems and optimization.
"""

import numpy as np
from .base import IdempotentSemiring


class MaxPlusSemiring(IdempotentSemiring):
    """Max-Plus semiring for continuous-valued FCA."""

    @property
    def zero(self) -> float:
        """Additive identity: -∞."""
        return float('-inf')

    @property
    def one(self) -> float:
        """Multiplicative identity: 0."""
        return 0.0

    def add(self, a: float, b: float) -> float:
        """Addition: max(a, b)."""
        return max(float(a), float(b))

    def multiply(self, a: float, b: float) -> float:
        """
        Multiplication: a + b (regular addition).
        Special case: -∞ + ∞ = -∞ (absorbing)
        """
        a, b = float(a), float(b)
        if a == float('-inf') or b == float('-inf'):
            return float('-inf')
        if np.isposinf(a) and np.isneginf(b):
            return float('-inf')
        if np.isneginf(a) and np.isposinf(b):
            return float('-inf')
        return a + b

    def leq(self, a: float, b: float) -> bool:
        """Natural order: a ≤ b ⟺ max(a, b) = b."""
        return float(a) <= float(b)

    def inverse(self, a: float) -> float:
        """
        Multiplicative inverse: -a (negation).
        For a ≠ ε, a ⊗ (-a) = a + (-a) = 0 = e.
        """
        if a == float('-inf'):
            raise ValueError("Cannot invert -∞")
        return -float(a)

    def left_residual(self, a: float, c: float) -> float:
        """
        Left residual: a\\c = c - a
        Finds λ such that a + λ ≤ c, giving λ ≤ c - a.
        Maximum is c - a.
        """
        a, c = float(a), float(c)
        if a == float('-inf'):
            return float('inf')
        if c == float('-inf'):
            return float('-inf')
        return c - a

    def right_residual(self, c: float, b: float) -> float:
        """
        Right residual: c/b = c - b
        (Commutative for Max-Plus since addition is commutative)
        """
        return self.left_residual(b, c)

    def __repr__(self):
        return "MaxPlusSemiring(ℝ∪{-∞,∞}, max, +, -∞, 0)"
