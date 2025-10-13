"""
K-Formal Concept Analysis (K-FCA) Implementation

A Python implementation of K-valued Formal Concept Analysis that generalizes
classical FCA to handle continuous and multi-valued attributes using idempotent
semirings.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .context import KValuedContext
from .galois import GaloisConnection
from .lattice import ConceptLattice

__all__ = ["KValuedContext", "GaloisConnection", "ConceptLattice"]
