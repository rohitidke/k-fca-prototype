"""
Unit tests for semiring implementations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.semirings import BooleanSemiring, MaxPlusSemiring, MinPlusSemiring


class TestBooleanSemiring:
    """Tests for Boolean semiring."""

    def setup_method(self):
        self.K = BooleanSemiring()

    def test_identities(self):
        assert self.K.zero == 0
        assert self.K.one == 1

    def test_addition(self):
        assert self.K.add(0, 0) == 0
        assert self.K.add(0, 1) == 1
        assert self.K.add(1, 0) == 1
        assert self.K.add(1, 1) == 1

    def test_multiplication(self):
        assert self.K.multiply(0, 0) == 0
        assert self.K.multiply(0, 1) == 0
        assert self.K.multiply(1, 0) == 0
        assert self.K.multiply(1, 1) == 1

    def test_idempotency(self):
        assert self.K.add(0, 0) == 0
        assert self.K.add(1, 1) == 1

    def test_natural_order(self):
        assert self.K.leq(0, 0)
        assert self.K.leq(0, 1)
        assert not self.K.leq(1, 0)
        assert self.K.leq(1, 1)

    def test_residuals(self):
        # Test left residual (implication)
        assert self.K.left_residual(0, 0) == 1
        assert self.K.left_residual(0, 1) == 1
        assert self.K.left_residual(1, 0) == 0
        assert self.K.left_residual(1, 1) == 1

    def test_matrix_multiply(self):
        A = np.array([[1, 0], [0, 1]], dtype=object)
        B = np.array([[1], [1]], dtype=object)
        result = self.K.matrix_multiply(A, B)
        expected = np.array([[1], [1]], dtype=object)
        assert np.array_equal(result, expected)


class TestMaxPlusSemiring:
    """Tests for Max-Plus semiring."""

    def setup_method(self):
        self.K = MaxPlusSemiring()

    def test_identities(self):
        assert self.K.zero == float('-inf')
        assert self.K.one == 0.0

    def test_addition(self):
        assert self.K.add(1, 2) == 2
        assert self.K.add(-5, 3) == 3
        assert self.K.add(float('-inf'), 5) == 5

    def test_multiplication(self):
        assert self.K.multiply(2, 3) == 5
        assert self.K.multiply(-2, 3) == 1
        assert self.K.multiply(0, 5) == 5
        assert self.K.multiply(float('-inf'), 5) == float('-inf')

    def test_idempotency(self):
        assert self.K.add(5, 5) == 5
        assert self.K.add(-3, -3) == -3

    def test_natural_order(self):
        assert self.K.leq(1, 2)
        assert self.K.leq(-5, 3)
        assert not self.K.leq(5, 2)

    def test_inverse(self):
        assert self.K.inverse(5) == -5
        assert self.K.inverse(-3) == 3
        assert self.K.inverse(0) == 0

    def test_residuals(self):
        assert self.K.left_residual(2, 5) == 3
        assert self.K.left_residual(3, 1) == -2


class TestMinPlusSemiring:
    """Tests for Min-Plus semiring."""

    def setup_method(self):
        self.K = MinPlusSemiring()

    def test_identities(self):
        assert self.K.zero == float('inf')
        assert self.K.one == 0.0

    def test_addition(self):
        assert self.K.add(1, 2) == 1
        assert self.K.add(-5, 3) == -5
        assert self.K.add(float('inf'), 5) == 5

    def test_multiplication(self):
        assert self.K.multiply(2, 3) == 5
        assert self.K.multiply(-2, 3) == 1
        assert self.K.multiply(0, 5) == 5
        assert self.K.multiply(float('inf'), 5) == float('inf')

    def test_idempotency(self):
        assert self.K.add(5, 5) == 5
        assert self.K.add(-3, -3) == -3

    def test_natural_order(self):
        assert self.K.leq(1, 2)
        assert self.K.leq(-5, 3)
        assert not self.K.leq(5, 2)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
