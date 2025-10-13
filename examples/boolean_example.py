"""
Boolean (Standard FCA) Example

This example demonstrates standard Formal Concept Analysis as a special
case of K-FCA where K = Boolean semiring and φ = 1.

Based on the classic example from Ganter & Wille (1999).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.context import KValuedContext
from src.galois import GaloisConnection
from src.lattice import ConceptLattice
from src.semirings import BooleanSemiring
from src.visualization import plot_context, plot_lattice, export_lattice_to_graphviz


def create_simple_context():
    """
    Create a simple Boolean context.

    Objects: 5 numbered items (1-5)
    Attributes: a, b, c, d
    """
    objects = ["1", "2", "3", "4", "5"]
    attributes = ["a", "b", "c", "d"]

    # Incidence relation (cross table from presentation)
    #     a  b  c  d
    # 1   ×  ×  ×  ×
    # 2   ×  ×  0  0
    # 3   0  ×  ×  ×
    # 4   0  ×  0  0
    # 5   0  ×  ×  0
    relation = np.array([
        [1, 1, 1, 1],  # Object 1
        [1, 1, 0, 0],  # Object 2
        [0, 1, 1, 1],  # Object 3
        [0, 1, 0, 0],  # Object 4
        [0, 1, 1, 0],  # Object 5
    ], dtype=object)

    semiring = BooleanSemiring()
    return KValuedContext(objects, attributes, relation, semiring)


def main():
    """Run the Boolean FCA example."""
    print("=" * 70)
    print("Standard FCA Example (Boolean Semiring)")
    print("=" * 70)
    print()

    # Create context
    context = create_simple_context()
    print(context)
    print()

    # Create Galois connection with pivot φ = 1
    galois = GaloisConnection(context, pivot=1)
    print(f"Galois Connection: {galois}")
    print()

    # Build concept lattice
    print("Building concept lattice...")
    lattice = ConceptLattice(context, galois, method="canonical")
    print(f"✓ Found {len(lattice)} concepts\n")

    # Display all concepts
    print("All Concepts:")
    print("=" * 70)

    for i in range(len(lattice.concepts)):
        concept = lattice.concepts[i]
        objs = lattice.get_concept_objects(i)
        attrs = lattice.get_concept_attributes(i)

        print(f"\nConcept #{i}:")
        print(f"  Extent:  {{ {', '.join(objs) if objs else '∅'} }}")
        print(f"  Intent:  {{ {', '.join(attrs) if attrs else '∅'} }}")

        # Show neighbors in Hasse diagram
        upper = [str(j) for j in lattice.upper_neighbors[i]]
        lower = [str(j) for j in lattice.lower_neighbors[i]]

        if upper:
            print(f"  Upper neighbors: {', '.join(upper)}")
        if lower:
            print(f"  Lower neighbors: {', '.join(lower)}")

    # Show top and bottom
    top = lattice.get_top_concept()
    bottom = lattice.get_bottom_concept()

    print("\n" + "=" * 70)
    print(f"Top concept (⊤):    Concept #{top}")
    print(f"Bottom concept (⊥): Concept #{bottom}")
    print("=" * 70)

    # Verify some concept properties
    print("\n" + "=" * 70)
    print("Verifying Concept Properties:")
    print("=" * 70)

    # Test object concept for "1"
    obj_vec = np.array([1, 0, 0, 0, 0], dtype=object)
    extent_1 = galois.extent_closure(obj_vec)
    intent_1 = galois.right_polar(extent_1)

    print(f"\nObject concept γ({{1}}):")
    print(f"  Extent: {context.get_objects_subset(extent_1)}")
    print(f"  Intent: {context.get_attributes_subset(intent_1)}")
    print(f"  Is concept: {galois.is_concept(extent_1, intent_1)}")

    # Test attribute concept for "b"
    attr_vec = np.array([0, 1, 0, 0], dtype=object)
    intent_b = galois.intent_closure(attr_vec)
    extent_b = galois.left_polar(intent_b)

    print(f"\nAttribute concept µ({{b}}):")
    print(f"  Extent: {context.get_objects_subset(extent_b)}")
    print(f"  Intent: {context.get_attributes_subset(intent_b)}")
    print(f"  Is concept: {galois.is_concept(extent_b, intent_b)}")

    # Visualizations
    print("\n" + "=" * 70)
    print("Generating visualizations...")
    print("=" * 70)

    # Plot context (auto-saved to output/contexts/)
    fig1 = plot_context(
        context,
        title="Boolean Formal Context",
        save_path="boolean_context.png"
    )
    print("✓ Saved: output/contexts/boolean_context.png")

    # Plot lattice with different layouts (auto-saved to output/lattices/)
    for layout in ["hierarchical", "spring"]:
        fig = plot_lattice(
            lattice,
            title=f"Concept Lattice ({layout} layout)",
            layout=layout,
            save_path=f"boolean_lattice_{layout}.png"
        )
        print(f"✓ Saved: output/lattices/boolean_lattice_{layout}.png")

    # Export to Graphviz (saved to output/exports/)
    export_lattice_to_graphviz(lattice, "boolean_lattice.dot")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
