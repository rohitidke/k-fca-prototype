"""
φ-Concept Lattice Builder

Constructs the concept lattice B_φ(G, M, R)_K for a K-valued formal context.

A φ-concept is a pair (a, b) where:
- a ⊆ G (extent: set of objects)
- b ⊆ M (intent: set of attributes)
- ⁻ᵩa = b and b⁻ᵩ = a (closure condition)

The lattice is ordered by: (a₁, b₁) ≤ (a₂, b₂) ⟺ a₁ ≤ a₂ ⟺ b₁ ≥^op b₂
"""

import numpy as np
from typing import List, Tuple, Set, Dict, Any, Optional
from dataclasses import dataclass
from .context import KValuedContext
from .galois import GaloisConnection


@dataclass(frozen=True, eq=True)
class Concept:
    """
    Represents a formal φ-concept.

    Attributes:
        extent_idx: Tuple of object indices
        intent_idx: Tuple of attribute indices
        extent_vec: Object vector (frozen as tuple)
        intent_vec: Attribute vector (frozen as tuple)
    """
    extent_idx: Tuple[int, ...]
    intent_idx: Tuple[int, ...]
    extent_vec: Tuple[Any, ...]  # Frozen numpy array as tuple
    intent_vec: Tuple[Any, ...]  # Frozen numpy array as tuple

    def __hash__(self):
        return hash((self.extent_idx, self.intent_idx))

    def __repr__(self):
        return f"Concept(extent={self.extent_idx}, intent={self.intent_idx})"


class ConceptLattice:
    """
    Builds and represents the φ-concept lattice for a K-valued context.

    The lattice is built by:
    1. Generating all possible object/attribute combinations
    2. Computing closures to find concepts
    3. Building the order relation between concepts
    """

    def __init__(
        self,
        context: KValuedContext,
        galois: GaloisConnection,
        method: str = "canonical"
    ):
        """
        Initialize and build the concept lattice.

        Args:
            context: The K-valued formal context
            galois: The Galois connection (with pivot)
            method: Algorithm to use ('canonical', 'objects', 'attributes')
        """
        self.context = context
        self.galois = galois
        self.semiring = context.semiring

        # Store concepts
        self.concepts: List[Concept] = []
        self.concept_map: Dict[Tuple, int] = {}  # Maps concept signature to index

        # Build lattice structure
        self.order: Dict[int, Set[int]] = {}  # concept_id -> {lower concepts}
        self.upper_neighbors: Dict[int, Set[int]] = {}  # Hasse diagram
        self.lower_neighbors: Dict[int, Set[int]] = {}

        # Build the lattice
        if method == "canonical":
            self._build_canonical()
        elif method == "objects":
            self._build_from_objects()
        elif method == "attributes":
            self._build_from_attributes()
        else:
            raise ValueError(f"Unknown method: {method}")

        self._compute_order()

    def _vector_to_indices(self, vec: np.ndarray) -> Tuple[int, ...]:
        """Convert a characteristic vector to tuple of indices where >= pivot threshold."""
        indices = []
        for i, val in enumerate(vec):
            # Include if val >= pivot (val not below pivot)
            # This properly thresholds fuzzy/continuous values
            if val != self.semiring.zero and (self.semiring.leq(self.galois.pivot, val) or val == self.semiring.one):
                indices.append(i)
        return tuple(sorted(indices))

    def _add_concept(self, extent: np.ndarray, intent: np.ndarray) -> Optional[int]:
        """
        Add a concept to the lattice if it doesn't exist.

        Args:
            extent: Object vector
            intent: Attribute vector

        Returns:
            Concept ID (index in concepts list), or None if already exists
        """
        # Verify it's actually a concept
        if not self.galois.is_concept(extent, intent):
            return None

        # Create signature
        extent_idx = self._vector_to_indices(extent)
        intent_idx = self._vector_to_indices(intent)
        signature = (extent_idx, intent_idx)

        # Check if exists
        if signature in self.concept_map:
            return self.concept_map[signature]

        # Create concept
        concept = Concept(
            extent_idx=extent_idx,
            intent_idx=intent_idx,
            extent_vec=tuple(extent),
            intent_vec=tuple(intent)
        )

        # Add to list
        concept_id = len(self.concepts)
        self.concepts.append(concept)
        self.concept_map[signature] = concept_id

        return concept_id

    def _build_from_objects(self):
        """
        Build lattice by computing object concepts.

        For each object g, compute γ({g}) to get a concept.
        """
        n = self.context.n_objects

        # Top concept (all objects, common attributes)
        all_objects = np.ones(n, dtype=object)
        for i in range(n):
            all_objects[i] = self.semiring.one
        top_intent = self.galois.right_polar(all_objects)
        self._add_concept(all_objects, top_intent)

        # Object concepts
        for i in range(n):
            # Singleton object
            obj_vec = np.array([self.semiring.zero] * n, dtype=object)
            obj_vec[i] = self.semiring.one

            # Compute closure
            extent = self.galois.extent_closure(obj_vec)
            intent = self.galois.right_polar(extent)
            self._add_concept(extent, intent)

        # Bottom concept (no objects, all attributes)
        zero_extent = np.array([self.semiring.zero] * n, dtype=object)
        all_attrs = np.ones(self.context.n_attributes, dtype=object)
        for j in range(self.context.n_attributes):
            all_attrs[j] = self.semiring.one
        bottom_extent = self.galois.left_polar(all_attrs)
        self._add_concept(bottom_extent, all_attrs)

    def _build_from_attributes(self):
        """
        Build lattice by computing attribute concepts.

        For each attribute m, compute µ({m}) to get a concept.
        """
        p = self.context.n_attributes

        # Bottom concept (common objects, all attributes)
        all_attrs = np.ones(p, dtype=object)
        for j in range(p):
            all_attrs[j] = self.semiring.one
        bottom_extent = self.galois.left_polar(all_attrs)
        self._add_concept(bottom_extent, all_attrs)

        # Attribute concepts
        for j in range(p):
            # Singleton attribute
            attr_vec = np.array([self.semiring.zero] * p, dtype=object)
            attr_vec[j] = self.semiring.one

            # Compute closure
            intent = self.galois.intent_closure(attr_vec)
            extent = self.galois.left_polar(intent)
            self._add_concept(extent, intent)

        # Top concept (all objects, common attributes)
        zero_intent = np.array([self.semiring.zero] * p, dtype=object)
        all_objs = np.ones(self.context.n_objects, dtype=object)
        for i in range(self.context.n_objects):
            all_objs[i] = self.semiring.one
        top_intent = self.galois.right_polar(all_objs)
        self._add_concept(all_objs, top_intent)

    def _build_canonical(self):
        """
        Build lattice using canonical base algorithm.

        Generates concepts from object and attribute concepts, then finds all concepts.
        """
        # Start with object and attribute concepts
        self._build_from_objects()
        self._build_from_attributes()

        # Find additional concepts through meets and joins
        # (This is a simplified version; full algorithm is more complex)
        max_iterations = 100
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            old_size = len(self.concepts)

            # Try to find new concepts by combining existing ones
            current_concepts = list(self.concepts)
            for i, c1 in enumerate(current_concepts):
                for c2 in current_concepts[i+1:]:
                    # Try meet in extent lattice
                    extent1 = np.array(c1.extent_vec, dtype=object)
                    extent2 = np.array(c2.extent_vec, dtype=object)

                    # Compute infimum (component-wise min in semiring order)
                    meet_extent = np.array([
                        e1 if self.semiring.leq(e1, e2) else e2
                        for e1, e2 in zip(extent1, extent2)
                    ], dtype=object)

                    # Close and add
                    closed_extent = self.galois.extent_closure(meet_extent)
                    intent = self.galois.right_polar(closed_extent)
                    self._add_concept(closed_extent, intent)

            # Check if we found new concepts
            if len(self.concepts) == old_size:
                break

    def _compute_order(self):
        """
        Compute the order relation between concepts.

        (a₁, b₁) ≤ (a₂, b₂) ⟺ a₁ ⊆ a₂ (extent-wise)
        """
        n_concepts = len(self.concepts)

        # Initialize order relations
        for i in range(n_concepts):
            self.order[i] = set()
            self.upper_neighbors[i] = set()
            self.lower_neighbors[i] = set()

        # Compute order
        for i in range(n_concepts):
            for j in range(n_concepts):
                if i == j:
                    continue

                c1, c2 = self.concepts[i], self.concepts[j]

                # Check if extent1 ⊆ extent2 (component-wise)
                extent1 = np.array(c1.extent_vec, dtype=object)
                extent2 = np.array(c2.extent_vec, dtype=object)

                is_leq = all(
                    self.semiring.leq(e1, e2)
                    for e1, e2 in zip(extent1, extent2)
                )

                if is_leq and not all(e1 == e2 for e1, e2 in zip(extent1, extent2)):
                    self.order[i].add(j)

        # Compute Hasse diagram (remove transitive edges)
        for i in range(n_concepts):
            candidates = self.order[i].copy()
            for j in self.order[i]:
                # Remove transitive connections
                candidates -= self.order[j]

            self.upper_neighbors[i] = candidates
            for j in candidates:
                self.lower_neighbors[j].add(i)

    def get_concept(self, concept_id: int) -> Concept:
        """Get concept by ID."""
        return self.concepts[concept_id]

    def get_concept_objects(self, concept_id: int) -> List[str]:
        """Get object names for a concept's extent."""
        concept = self.concepts[concept_id]
        return [self.context.objects[i] for i in concept.extent_idx]

    def get_concept_attributes(self, concept_id: int) -> List[str]:
        """Get attribute names for a concept's intent."""
        concept = self.concepts[concept_id]
        return [self.context.attributes[j] for j in concept.intent_idx]

    def get_top_concept(self) -> int:
        """Find the top concept (supremum)."""
        # Top has maximum extent
        max_size = max(len(c.extent_idx) for c in self.concepts)
        for i, c in enumerate(self.concepts):
            if len(c.extent_idx) == max_size:
                return i
        return 0

    def get_bottom_concept(self) -> int:
        """Find the bottom concept (infimum)."""
        # Bottom has minimum extent (usually empty)
        min_size = min(len(c.extent_idx) for c in self.concepts)
        for i, c in enumerate(self.concepts):
            if len(c.extent_idx) == min_size:
                return i
        return len(self.concepts) - 1

    def __len__(self):
        """Number of concepts in the lattice."""
        return len(self.concepts)

    def __repr__(self):
        return (
            f"ConceptLattice(\n"
            f"  Concepts: {len(self.concepts)},\n"
            f"  Context: {self.context.n_objects} objects × {self.context.n_attributes} attributes,\n"
            f"  Pivot: {self.galois.pivot}\n"
            f")"
        )
