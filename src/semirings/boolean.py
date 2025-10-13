"""
Boolean Semiring Implementation

B = ({0, 1}, ∨, ∧, 0, 1)

This is the standard Boolean algebra where:
- Addition (⊕) is logical OR (∨)
- Multiplication (⊗) is logical AND (∧)
- Zero (ε) is False (0)
- One (e) is True (1)

Standard FCA is K-FCA where K = B and φ = 1.
"""

from .base import IdempotentSemiring


class BooleanSemiring(IdempotentSemiring):
    """Boolean semiring for standard Formal Concept Analysis."""

    @property
    def zero(self) -> int:
        """Additive identity: 0 (False)."""
        return 0

    @property
    def one(self) -> int:
        """Multiplicative identity: 1 (True)."""
        return 1

    def add(self, a: int, b: int) -> int:
        """Addition: a ∨ b (logical OR)."""
        return max(int(a), int(b))

    def multiply(self, a: int, b: int) -> int:
        """Multiplication: a ∧ b (logical AND)."""
        return min(int(a), int(b))

    def leq(self, a: int, b: int) -> bool:
        """Natural order: a ≤ b ⟺ a ∨ b = b."""
        return self.add(a, b) == b

    def left_residual(self, a: int, c: int) -> int:
        """
        Left residual (implication): a\\c = a → c

        Truth table:
        a | c | a→c
        0 | 0 | 1
        0 | 1 | 1
        1 | 0 | 0
        1 | 1 | 1
        """
        a, c = int(a), int(c)
        if a == 0:
            return 1
        else:
            return c

    def right_residual(self, c: int, b: int) -> int:
        """
        Right residual: c/b = c → b
        (Commutative for Boolean semiring)
        """
        return self.left_residual(b, c)

    def negate(self, a: int) -> int:
        """Negation: ¬a = a → 0 = 0/a."""
        return self.left_residual(a, self.zero)

    def __repr__(self):
        return "BooleanSemiring(B, ∨, ∧, 0, 1)"
