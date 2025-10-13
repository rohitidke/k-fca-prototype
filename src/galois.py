"""
Galois Connections and φ-Polar Operators

For a K-valued context (G, M, R)_K and pivot φ ∈ K, we define:

φ-polars (contravariant adjunction):
  y⁻ᵩ = ⋀{ x ∈ X | ⟨y|x⟩_R ≥ φ }  (attributes to objects)
  ⁻ᵩx = ⋀{ y ∈ Y | ⟨y|x⟩_R ≥ φ }  (objects to attributes)

where the bracket is: ⟨y|x⟩_R = yᵗ · R · xᵗ (using semiring operations)

These form a Galois connection: X ⇌ Y^op

A φ-concept is a pair (a, b) where ⁻ᵩa = b and b⁻ᵩ = a (fixed points).
"""

import numpy as np
from typing import Tuple, Any
from .context import KValuedContext
from .semirings.base import IdempotentSemiring


class GaloisConnection:
    """
    Implements the Galois connection induced by a K-valued context and pivot.

    The φ-polar operators map between sets of objects and sets of attributes,
    forming closure operators that identify formal concepts.
    """

    def __init__(self, context: KValuedContext, pivot: Any = None):
        """
        Initialize Galois connection for a context with given pivot.

        Args:
            context: The K-valued formal context
            pivot: The threshold value φ ∈ K (default: semiring unit)

        For Boolean semiring: pivot = 1 (standard FCA)
        For semifields: pivot = e (multiplicative identity)
        """
        self.context = context
        self.semiring = context.semiring

        # Set default pivot
        if pivot is None:
            # For Boolean: use 1 (opposite semiring's zero)
            # For others: use multiplicative identity
            if hasattr(self.semiring, 'one'):
                self.pivot = self.semiring.one
            else:
                self.pivot = self.semiring.one
        else:
            self.pivot = pivot

    def bracket(self, y: np.ndarray, x: np.ndarray) -> Any:
        """
        Compute the bracket ⟨y|x⟩_R = (y^op·R)^op\φ for the opposite semiring.

        In practice, for standard Boolean semiring:
          ⟨y|x⟩ = yᵗ · R · xᵗ (matrix multiplication)

        Args:
            y: Attribute vector (p×1)
            x: Object vector (n×1)

        Returns:
            Value in K representing the degree of relation
        """
        R = self.context.relation

        # Ensure vectors are column vectors
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        if x.ndim == 1:
            x = x.reshape(-1, 1)

        # Compute yᵗ · R (results in 1×n)
        y_R = self.semiring.matrix_multiply(y.T, R)

        # Compute (yᵗ · R) · xᵗ (results in 1×1)
        result = self.semiring.matrix_multiply(y_R, x)

        return result.item() if result.size == 1 else result

    def left_polar(self, y: np.ndarray) -> np.ndarray:
        """
        Left polar (intent to extent): y⁻ᵩ

        y⁻ᵩ = ⋀{ x ∈ X | ⟨y|x⟩_R ≥ φ }

        This is computed as: y⁻ᵩ = φ^op / (R^op ← y)
        which simplifies to checking each object.

        Args:
            y: Attribute vector (intent) of shape (p,)

        Returns:
            Object vector (extent) of shape (n,)
        """
        R = self.context.relation
        n = self.context.n_objects

        # Result extent
        extent = np.zeros(n, dtype=object)

        # For each object
        for i in range(n):
            # Check if all attributes with degree y[j] are present
            # Compute: ⋀_j (R[i,j] / y[j]) and compare with pivot
            values = []
            for j in range(self.context.n_attributes):
                if y[j] != self.semiring.zero:
                    # Use right residual: R[i,j] / y[j]
                    residual = self.semiring.right_residual(R[i, j], y[j])
                    values.append(residual)

            # Take infimum (for opposite semiring = supremum in original)
            if values:
                result = values[0]
                for v in values[1:]:
                    # For Boolean: min corresponds to ∧
                    if self.semiring.leq(v, result):
                        result = v
                extent[i] = result
            else:
                extent[i] = self.semiring.one

        return extent

    def right_polar(self, x: np.ndarray) -> np.ndarray:
        """
        Right polar (extent to intent): ⁻ᵩx

        ⁻ᵩx = ⋀{ y ∈ Y | ⟨y|x⟩_R ≥ φ }

        This is computed as: ⁻ᵩx = (R ← x) \ φ

        Args:
            x: Object vector (extent) of shape (n,)

        Returns:
            Attribute vector (intent) of shape (p,)
        """
        R = self.context.relation
        p = self.context.n_attributes

        # Result intent
        intent = np.zeros(p, dtype=object)

        # For each attribute
        for j in range(p):
            # Check if all objects with degree x[i] satisfy the attribute
            # Compute: ⋀_i (x[i] \ R[i,j]) and compare with pivot
            values = []
            for i in range(self.context.n_objects):
                if x[i] != self.semiring.zero:
                    # Use left residual: x[i] \ R[i,j]
                    residual = self.semiring.left_residual(x[i], R[i, j])
                    values.append(residual)

            # Take infimum (for opposite semiring)
            if values:
                result = values[0]
                for v in values[1:]:
                    if self.semiring.leq(v, result):
                        result = v
                intent[j] = result
            else:
                intent[j] = self.semiring.one

        return intent

    def extent_closure(self, x: np.ndarray) -> np.ndarray:
        """
        Closure operator on extents: γ(x) = (⁻ᵩx)⁻ᵩ

        Args:
            x: Object vector (extent)

        Returns:
            Closed extent
        """
        intent = self.right_polar(x)
        return self.left_polar(intent)

    def intent_closure(self, y: np.ndarray) -> np.ndarray:
        """
        Closure operator on intents: κ*(y) = ⁻ᵩ(y⁻ᵩ)

        Args:
            y: Attribute vector (intent)

        Returns:
            Closed intent
        """
        extent = self.left_polar(y)
        return self.right_polar(extent)

    def is_closed_extent(self, x: np.ndarray) -> bool:
        """Check if an extent is closed: γ(x) = x."""
        closed = self.extent_closure(x)
        return np.array_equal(x, closed)

    def is_closed_intent(self, y: np.ndarray) -> bool:
        """Check if an intent is closed: κ*(y) = y."""
        closed = self.intent_closure(y)
        return np.array_equal(y, closed)

    def is_concept(self, extent: np.ndarray, intent: np.ndarray) -> bool:
        """
        Check if (extent, intent) forms a φ-concept.

        A pair (a, b) is a φ-concept iff:
          ⁻ᵩa = b AND b⁻ᵩ = a

        Args:
            extent: Object vector (a)
            intent: Attribute vector (b)

        Returns:
            True if (extent, intent) is a φ-concept
        """
        computed_intent = self.right_polar(extent)
        computed_extent = self.left_polar(intent)

        return (np.array_equal(computed_intent, intent) and
                np.array_equal(computed_extent, extent))

    def __repr__(self):
        return f"GaloisConnection(pivot={self.pivot}, semiring={self.semiring})"
