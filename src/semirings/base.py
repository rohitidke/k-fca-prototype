"""
Base class for idempotent semirings.

An idempotent semiring K = (K, ⊕, ⊗, ε, e) where:
- (K, ⊕, ε) is a commutative, idempotent monoid
- (K\{ε}, ⊗, e) is a monoid
- ⊗ distributes over ⊕
- a ⊕ a = a (idempotent property)
- Natural order: a ≤ b ⟺ a ⊕ b = b
"""

from abc import ABC, abstractmethod
from typing import Any
import numpy as np


class IdempotentSemiring(ABC):
    """Abstract base class for idempotent semirings."""

    @property
    @abstractmethod
    def zero(self) -> Any:
        """The additive identity (ε) - bottom element in natural order."""
        pass

    @property
    @abstractmethod
    def one(self) -> Any:
        """The multiplicative identity (e)."""
        pass

    @abstractmethod
    def add(self, a: Any, b: Any) -> Any:
        """
        Addition operation (⊕) - corresponds to join/max in natural order.
        Must be commutative, associative, and idempotent.
        """
        pass

    @abstractmethod
    def multiply(self, a: Any, b: Any) -> Any:
        """
        Multiplication operation (⊗).
        Must be associative and distribute over addition.
        """
        pass

    @abstractmethod
    def leq(self, a: Any, b: Any) -> bool:
        """
        Natural order: a ≤ b ⟺ a ⊕ b = b
        """
        pass

    @abstractmethod
    def left_residual(self, a: Any, c: Any) -> Any:
        """
        Left residual: a\\c = ⋁{λ ∈ K | a⊗λ ≤ c}
        Also called "under" operation.
        """
        pass

    @abstractmethod
    def right_residual(self, c: Any, b: Any) -> Any:
        """
        Right residual: c/b = ⋁{λ ∈ K | λ⊗b ≤ c}
        Also called "over" operation.
        """
        pass

    def sum(self, values):
        """
        Sum multiple values using the addition operation.
        Equivalent to supremum in the natural order.
        """
        if isinstance(values, np.ndarray):
            values = values.flatten()
        result = self.zero
        for v in values:
            result = self.add(result, v)
        return result

    def product(self, values):
        """Product multiple values using the multiplication operation."""
        if isinstance(values, np.ndarray):
            values = values.flatten()
        result = self.one
        for v in values:
            result = self.multiply(result, v)
        return result

    def matrix_multiply(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """
        Matrix multiplication in the semiring.
        (A ⊗ B)ij = ⊕k (Aik ⊗ Bkj)
        """
        if A.ndim == 1:
            A = A.reshape(1, -1)
        if B.ndim == 1:
            B = B.reshape(-1, 1)

        m, n = A.shape
        n2, p = B.shape

        if n != n2:
            raise ValueError(f"Matrix dimensions don't match: {A.shape} and {B.shape}")

        result = np.zeros((m, p), dtype=object)

        for i in range(m):
            for j in range(p):
                products = [self.multiply(A[i, k], B[k, j]) for k in range(n)]
                result[i, j] = self.sum(products)

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}(ε={self.zero}, e={self.one})"
