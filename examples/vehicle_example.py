"""
Vehicle Dataset Example

This example implements the vehicle dataset from the K-FCA presentation:
- 10 vehicles (objects)
- 11 attributes
- Values normalized between 0 and 1 in 0.25 steps [0, 0.25, 0.5, 0.75, 1]
- Based on 4 votes per context

Demonstrates K-FCA with Boolean semiring and continuous values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from src.context import KValuedContext
from src.galois import GaloisConnection
from src.lattice import ConceptLattice
from src.semirings import BooleanSemiring
from src.visualization import plot_context, plot_lattice


def create_vehicle_context():
    """
    Create the vehicle dataset context.

    Objects: 10 vehicles
    Attributes: 11 features
    Values: {0, 0.25, 0.5, 0.75, 1.0}
    """
    # Define objects (vehicles)
    objects = [
        "Car",
        "Boat",
        "Scooter",
        "Motorbike",
        "Bus",
        "Truck",
        "Van",
        "Bicycle",
        "Helicopter",
        "Airplane"
    ]

    # Define attributes
    attributes = [
        "is_transport",      # is a means of transportation
        "goes_fast",         # goes fast
        "is_big",           # is big
        "produces_noise",    # produces noise
        "has_2_wheels",     # has 2 wheels
        "has_4_wheels",     # has 4 wheels
        "has_motor",        # has motor
        "flies",            # can fly
        "floats",           # can float/sail
        "eco_friendly",     # environmentally friendly
        "expensive"         # expensive to buy/maintain
    ]

    # Define the incidence relation (based on normalized votes)
    # Each value represents the degree to which an object has an attribute
    relation = np.array([
        # is_trans goes_fast is_big noise 2whl 4whl motor flies floats eco expensive
        [1.00,    1.00,     0.50,  0.75, 0.00, 1.00, 1.00, 0.00, 0.00, 0.25, 0.75],  # Car
        [1.00,    0.50,     0.50,  0.50, 0.00, 0.00, 1.00, 0.00, 1.00, 0.50, 0.75],  # Boat
        [1.00,    0.50,     0.00,  0.50, 1.00, 0.00, 1.00, 0.00, 0.00, 0.50, 0.25],  # Scooter
        [1.00,    0.75,     0.00,  0.75, 1.00, 0.00, 1.00, 0.00, 0.00, 0.25, 0.50],  # Motorbike
        [1.00,    0.50,     1.00,  0.75, 0.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.50],  # Bus
        [1.00,    0.50,     1.00,  0.75, 0.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.75],  # Truck
        [1.00,    0.50,     0.75,  0.75, 0.00, 1.00, 1.00, 0.00, 0.00, 0.25, 0.75],  # Van
        [1.00,    0.25,     0.00,  0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00],  # Bicycle
        [1.00,    0.75,     0.50,  1.00, 0.00, 0.00, 1.00, 1.00, 0.00, 0.00, 1.00],  # Helicopter
        [1.00,    1.00,     1.00,  1.00, 0.00, 0.00, 1.00, 1.00, 0.00, 0.00, 1.00],  # Airplane
    ], dtype=object)

    # Create context with Boolean semiring
    # For continuous K-FCA, we'd use a different semiring
    semiring = BooleanSemiring()

    # For Boolean FCA, convert to binary using threshold
    # We'll create multiple contexts with different thresholds
    return objects, attributes, relation, semiring


def threshold_context(relation, threshold=0.75):
    """
    Convert continuous relation to binary using threshold.

    Args:
        relation: Continuous-valued relation matrix
        threshold: Values >= threshold become 1, else 0

    Returns:
        Binary relation matrix
    """
    binary = np.zeros_like(relation, dtype=object)
    for i in range(relation.shape[0]):
        for j in range(relation.shape[1]):
            binary[i, j] = 1 if relation[i, j] >= threshold else 0
    return binary


def main():
    """Run the vehicle example."""
    print("=" * 70)
    print("K-FCA Vehicle Dataset Example")
    print("=" * 70)
    print()

    # Create context
    objects, attributes, relation, semiring = create_vehicle_context()

    # Demonstrate with different thresholds
    thresholds = [0.5, 0.75, 1.0]

    for threshold in thresholds:
        print(f"\n{'='*70}")
        print(f"Threshold φ = {threshold}")
        print(f"{'='*70}\n")

        # Create binary context
        binary_relation = threshold_context(relation, threshold)
        context = KValuedContext(objects, attributes, binary_relation, semiring)

        print(context)
        print()

        # Create Galois connection with pivot φ = 1 (standard FCA)
        galois = GaloisConnection(context, pivot=1)

        # Build concept lattice
        print("Building concept lattice...")
        lattice = ConceptLattice(context, galois, method="objects")
        print(f"Found {len(lattice)} concepts\n")

        # Display some concepts
        print("Sample Concepts:")
        print("-" * 70)

        for i in range(min(5, len(lattice.concepts))):
            concept = lattice.concepts[i]
            objs = lattice.get_concept_objects(i)
            attrs = lattice.get_concept_attributes(i)

            print(f"\nConcept #{i}:")
            print(f"  Extent (Objects):    {objs if objs else '∅'}")
            print(f"  Intent (Attributes): {attrs if attrs else '∅'}")

        # Find interesting concepts
        print("\n" + "-" * 70)
        print("Interesting Concepts:")
        print("-" * 70)

        # Find concept for "has motor"
        for i, concept in enumerate(lattice.concepts):
            attrs = lattice.get_concept_attributes(i)
            if "has_motor" in attrs and len(attrs) <= 3:
                objs = lattice.get_concept_objects(i)
                print(f"\nConcept with 'has_motor':")
                print(f"  Objects: {objs}")
                print(f"  Attributes: {attrs}")
                break

        # Find concept for "4 wheels"
        for i, concept in enumerate(lattice.concepts):
            attrs = lattice.get_concept_attributes(i)
            if "has_4_wheels" in attrs and len(attrs) <= 3:
                objs = lattice.get_concept_objects(i)
                print(f"\nConcept with 'has_4_wheels':")
                print(f"  Objects: {objs}")
                print(f"  Attributes: {attrs}")
                break

        # Visualizations
        print(f"\n{'='*70}")
        print("Generating visualizations...")
        print(f"{'='*70}\n")

        # Plot context (auto-saved to output/contexts/)
        fig1 = plot_context(
            context,
            title=f"Vehicle Context (threshold φ = {threshold})",
            save_path=f"vehicle_context_phi_{threshold}.png"
        )
        print(f"✓ Saved: output/contexts/vehicle_context_phi_{threshold}.png")

        # Plot lattice (auto-saved to output/lattices/)
        fig2 = plot_lattice(
            lattice,
            title=f"Vehicle Concept Lattice (φ = {threshold})",
            layout="hierarchical",
            save_path=f"vehicle_lattice_phi_{threshold}.png"
        )
        print(f"✓ Saved: output/lattices/vehicle_lattice_phi_{threshold}.png")

        # Export to Graphviz
        export_lattice_to_graphviz(lattice, f"vehicle_lattice_phi_{threshold}.dot")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
