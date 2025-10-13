"""
K-Valued Formal Context

Definition: A K-valued formal context is a triple (G, M, R)_K where:
- G is a finite set of objects (|G| = n)
- M is a finite set of attributes (|M| = p)
- K is an idempotent semiring
- R ∈ K^(n×p) is the K-valued incidence relation

R(g,m) = λ reads: "object g has attribute m to degree λ"
Dually: "attribute m is manifested in object g to degree λ"
"""

import numpy as np
from typing import List, Optional, Dict, Any
from .semirings.base import IdempotentSemiring


class KValuedContext:
    """
    Represents a K-valued formal context (G, M, R)_K.

    Attributes:
        objects: List of object names
        attributes: List of attribute names
        relation: Matrix R ∈ K^(n×p) with incidence values
        semiring: The idempotent semiring K
    """

    def __init__(
        self,
        objects: List[str],
        attributes: List[str],
        relation: np.ndarray,
        semiring: IdempotentSemiring,
    ):
        """
        Initialize a K-valued formal context.

        Args:
            objects: List of object names (length n)
            attributes: List of attribute names (length p)
            relation: Matrix R of shape (n, p) with K-values
            semiring: The idempotent semiring K

        Raises:
            ValueError: If dimensions don't match
        """
        self.objects = list(objects)
        self.attributes = list(attributes)
        self.semiring = semiring

        # Validate dimensions
        n, p = len(objects), len(attributes)
        if relation.shape != (n, p):
            raise ValueError(
                f"Relation shape {relation.shape} doesn't match "
                f"objects×attributes ({n}×{p})"
            )

        # Convert to object array to store semiring values
        self.relation = np.array(relation, dtype=object)

        # Create index mappings
        self.object_index = {obj: i for i, obj in enumerate(objects)}
        self.attribute_index = {attr: j for j, attr in enumerate(attributes)}

    @property
    def n_objects(self) -> int:
        """Number of objects (n)."""
        return len(self.objects)

    @property
    def n_attributes(self) -> int:
        """Number of attributes (p)."""
        return len(self.attributes)

    def get_incidence(self, obj: str, attr: str) -> Any:
        """
        Get the incidence value R(g, m).

        Args:
            obj: Object name
            attr: Attribute name

        Returns:
            The incidence value in K
        """
        i = self.object_index[obj]
        j = self.attribute_index[attr]
        return self.relation[i, j]

    def set_incidence(self, obj: str, attr: str, value: Any):
        """
        Set the incidence value R(g, m) = value.

        Args:
            obj: Object name
            attr: Attribute name
            value: The incidence value in K
        """
        i = self.object_index[obj]
        j = self.attribute_index[attr]
        self.relation[i, j] = value

    def get_object_vector(self, obj: str) -> np.ndarray:
        """
        Get the row vector for an object (object description).

        Args:
            obj: Object name

        Returns:
            Row vector of shape (p,)
        """
        i = self.object_index[obj]
        return self.relation[i, :]

    def get_attribute_vector(self, attr: str) -> np.ndarray:
        """
        Get the column vector for an attribute (attribute description).

        Args:
            attr: Attribute name

        Returns:
            Column vector of shape (n,)
        """
        j = self.attribute_index[attr]
        return self.relation[:, j]

    def get_objects_subset(self, object_vector: np.ndarray) -> List[str]:
        """
        Convert a characteristic vector to list of object names.

        Args:
            object_vector: Binary/K-valued vector of shape (n,)

        Returns:
            List of object names where vector is non-zero
        """
        result = []
        for i, val in enumerate(object_vector):
            if not self.semiring.leq(val, self.semiring.zero) and val != self.semiring.zero:
                result.append(self.objects[i])
        return result

    def get_attributes_subset(self, attribute_vector: np.ndarray) -> List[str]:
        """
        Convert a characteristic vector to list of attribute names.

        Args:
            attribute_vector: Binary/K-valued vector of shape (p,)

        Returns:
            List of attribute names where vector is non-zero
        """
        result = []
        for j, val in enumerate(attribute_vector):
            if not self.semiring.leq(val, self.semiring.zero) and val != self.semiring.zero:
                result.append(self.attributes[j])
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Export context as dictionary."""
        return {
            "objects": self.objects,
            "attributes": self.attributes,
            "relation": self.relation.tolist(),
            "semiring": str(self.semiring),
        }

    def __repr__(self):
        return (
            f"KValuedContext(\n"
            f"  Objects: {self.n_objects},\n"
            f"  Attributes: {self.n_attributes},\n"
            f"  Semiring: {self.semiring}\n"
            f")"
        )

    def __str__(self):
        """Pretty print the context as a table."""
        # Header
        lines = ["K-Valued Formal Context", "=" * 50]
        lines.append(f"Semiring: {self.semiring}")
        lines.append("")

        # Table header
        col_width = max(len(obj) for obj in self.objects) + 2
        header = " " * col_width + " | " + " | ".join(f"{attr:^8}" for attr in self.attributes)
        lines.append(header)
        lines.append("-" * len(header))

        # Table rows
        for i, obj in enumerate(self.objects):
            row = f"{obj:<{col_width}} | "
            row += " | ".join(f"{self.relation[i, j]:^8}" for j in range(self.n_attributes))
            lines.append(row)

        return "\n".join(lines)
