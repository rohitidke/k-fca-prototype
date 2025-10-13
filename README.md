# K-Formal Concept Analysis (K-FCA) Prototype

A Python implementation of **K-valued Formal Concept Analysis** that generalizes classical FCA to handle continuous and multi-valued attributes using idempotent semirings.

## Overview

K-FCA extends traditional Formal Concept Analysis from Boolean domains to arbitrary idempotent semirings, allowing analysis of:
- **Continuous data** (real-valued attributes)
- **Multi-valued data** (degrees of membership)
- **Fuzzy data** (uncertainty and partial truth)

**Key Innovation**: Instead of binary (yes/no) relationships, K-FCA handles degrees of membership using mathematical structures called **idempotent semirings**.

## Features

- ✅ **Multiple Semirings**: Boolean, Max-Plus, Min-Plus (easily extensible)
- ✅ **K-Valued Contexts**: Support for continuous and multi-valued attributes
- ✅ **Galois Connections**: φ-polar operators for computing extents and intents
- ✅ **Concept Lattice Builder**: Automated extraction of φ-concepts
- ✅ **Visualization**: Heatmaps for contexts and Hasse diagrams for lattices
- ✅ **Examples**: Vehicle dataset and classical FCA examples

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd k-fca-prototype

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Example 1: Boolean (Standard FCA)

```python
import numpy as np
from src.context import KValuedContext
from src.galois import GaloisConnection
from src.lattice import ConceptLattice
from src.semirings import BooleanSemiring

# Define context
objects = ["1", "2", "3", "4", "5"]
attributes = ["a", "b", "c", "d"]
relation = np.array([
    [1, 1, 1, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 1],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
], dtype=object)

# Create K-valued context
semiring = BooleanSemiring()
context = KValuedContext(objects, attributes, relation, semiring)

# Build concept lattice
galois = GaloisConnection(context, pivot=1)
lattice = ConceptLattice(context, galois)

print(f"Found {len(lattice)} concepts")
```

### Example 2: Vehicle Dataset (Continuous Values)

```python
# Run the vehicle example
cd examples
python vehicle_example.py
```

This example demonstrates K-FCA on the vehicle dataset with:
- 10 vehicles (Car, Boat, Scooter, ...)
- 11 attributes (is_transport, goes_fast, is_big, ...)
- Values in [0, 0.25, 0.5, 0.75, 1.0]

## Project Structure

```
k-fca-prototype/
├── src/
│   ├── __init__.py
│   ├── semirings/
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract idempotent semiring
│   │   ├── boolean.py         # Boolean semiring (standard FCA)
│   │   ├── maxplus.py         # Max-Plus semiring
│   │   └── minplus.py         # Min-Plus semiring
│   ├── context.py             # K-valued formal context
│   ├── galois.py              # Galois connections & φ-polars
│   ├── lattice.py             # Concept lattice builder
│   └── visualization.py       # Plotting utilities
├── examples/
│   ├── vehicle_example.py     # Vehicle dataset from presentation
│   ├── boolean_example.py     # Standard FCA example
│   └── tutorial.ipynb         # Interactive Jupyter tutorial
├── output/                    # Generated visualizations & exports
│   ├── contexts/              # Context heatmaps
│   ├── lattices/              # Lattice Hasse diagrams
│   ├── concepts/              # Individual concept details
│   └── exports/               # DOT files, JSON, CSV
├── tests/
│   ├── __init__.py
│   └── test_semirings.py      # Unit tests
├── requirements.txt
└── README.md
```

## Mathematical Background

### Idempotent Semirings

An **idempotent semiring** K = (K, ⊕, ⊗, ε, e) consists of:
- Addition (⊕): Commutative, idempotent monoid with identity ε
- Multiplication (⊗): Monoid with identity e
- Natural order: a ≤ b ⟺ a ⊕ b = b

**Examples**:

| Semiring | Set K | ⊕ (join) | ⊗ (meet) | ε | e |
|----------|-------|----------|----------|---|---|
| Boolean  | {0,1} | ∨ (or)   | ∧ (and)  | 0 | 1 |
| Max-Plus | ℝ∪{-∞,∞} | max   | +        | -∞ | 0 |
| Min-Plus | ℝ∪{-∞,∞} | min   | +        | ∞  | 0 |

### K-Valued Formal Context

**Definition**: A K-valued formal context is a triple (G, M, R)_K where:
- G is a finite set of objects (|G| = n)
- M is a finite set of attributes (|M| = p)
- K is an idempotent semiring
- R ∈ K^(n×p) is the K-valued incidence relation

R(g,m) = λ reads: "*object g has attribute m to degree λ*"

### φ-Polar Operators

For a pivot φ ∈ K, we define:

```
y⁻ᵩ = ⋀{ x ∈ X | ⟨y|x⟩_R ≥ φ }  (attributes → objects)
⁻ᵩx = ⋀{ y ∈ Y | ⟨y|x⟩_R ≥ φ }  (objects → attributes)
```

These form a **Galois connection** between object and attribute spaces.

### φ-Concepts

A pair (a, b) is a **φ-concept** if:
- a is the extent (set of objects)
- b is the intent (set of attributes)
- ⁻ᵩa = b and b⁻ᵩ = a (closure condition)

The set of all φ-concepts forms a **complete lattice** ordered by extent inclusion.

## Usage Examples

### Creating a Custom Semiring

```python
from src.semirings.base import IdempotentSemiring

class CustomSemiring(IdempotentSemiring):
    @property
    def zero(self):
        return 0  # Additive identity

    @property
    def one(self):
        return 1  # Multiplicative identity

    def add(self, a, b):
        return max(a, b)  # Join operation

    def multiply(self, a, b):
        return min(a, b)  # Meet operation

    # Implement other abstract methods...
```

### Computing Extents and Intents

```python
# Create context and Galois connection
context = KValuedContext(objects, attributes, relation, semiring)
galois = GaloisConnection(context, pivot=0.75)

# Compute extent for a set of objects
object_vec = np.array([1, 1, 0, 0, 0], dtype=object)
extent = galois.extent_closure(object_vec)
intent = galois.right_polar(extent)

print(f"Extent: {context.get_objects_subset(extent)}")
print(f"Intent: {context.get_attributes_subset(intent)}")
```

### Visualizing Results

```python
from src.visualization import plot_context, plot_lattice

# Plot context as heatmap
fig1 = plot_context(context, title="My Context")
fig1.savefig("context.png")

# Plot lattice as Hasse diagram
fig2 = plot_lattice(lattice, layout="hierarchical")
fig2.savefig("lattice.png")
```

## Running Examples

### Boolean Example (Standard FCA)
```bash
cd examples
python boolean_example.py
```

Output:
- Context visualization
- Complete concept lattice
- All concepts with extents and intents

### Vehicle Example
```bash
cd examples
python vehicle_example.py
```

Output:
- Multiple contexts with different thresholds (φ = 0.5, 0.75, 1.0)
- Concept lattices for each threshold
- All visualizations saved to `output/` directory

## Output Directory Structure

All generated visualizations and exports are organized in the `output/` directory:

```
output/
├── contexts/     # Context heatmaps (PNG)
├── lattices/     # Lattice Hasse diagrams (PNG)
├── concepts/     # Individual concept details (PNG)
└── exports/      # Graphviz DOT files, JSON, CSV
```

**Example outputs:**
- `output/contexts/boolean_context.png` - Context heatmap
- `output/lattices/vehicle_lattice_phi_0.75.png` - Lattice diagram
- `output/exports/boolean_lattice.dot` - Graphviz export

See [`output/README.md`](output/README.md) for detailed documentation on the output structure.

**Note:** Output files are `.gitignore`d to keep the repository clean. Only the directory structure is tracked.

## API Reference

### Core Classes

#### `KValuedContext`
Represents a K-valued formal context (G, M, R)_K.

**Methods**:
- `get_incidence(obj, attr)`: Get incidence value R(g,m)
- `get_object_vector(obj)`: Get row vector for object
- `get_attribute_vector(attr)`: Get column vector for attribute

#### `GaloisConnection`
Implements φ-polar operators and closure operators.

**Methods**:
- `left_polar(y)`: Compute y⁻ᵩ (intent → extent)
- `right_polar(x)`: Compute ⁻ᵩx (extent → intent)
- `extent_closure(x)`: Compute closure γ(x)
- `is_concept(extent, intent)`: Verify if pair is a concept

#### `ConceptLattice`
Builds and represents the concept lattice.

**Methods**:
- `get_concept(id)`: Get concept by ID
- `get_concept_objects(id)`: Get object names for extent
- `get_concept_attributes(id)`: Get attribute names for intent
- `get_top_concept()`: Find supremum
- `get_bottom_concept()`: Find infimum

### Semiring Classes

- `BooleanSemiring`: Standard FCA ({0,1}, ∨, ∧)
- `MaxPlusSemiring`: Tropical semiring (ℝ∪{-∞,∞}, max, +)
- `MinPlusSemiring`: Arctic semiring (ℝ∪{-∞,∞}, min, +)

## Testing

```bash
# Run tests (coming soon)
pytest tests/
```

## Theory vs. Implementation

**Standard FCA** is K-FCA where:
- K = Boolean semiring ({0, 1}, ∨, ∧, 0, 1)
- φ = 1 (complete membership required)
- Relations are binary (object has/doesn't have attribute)

**K-FCA generalizes** this by:
- Allowing arbitrary idempotent semirings K
- Supporting continuous degrees of membership
- Tunable pivot φ for different analysis levels

## References

1. **Valverde-Albacete & Peláez-Moreno** (2001): "Towards a Generalisation of Formal Concept Analysis for Data Mining purposes"
2. **Ganter & Wille** (1999): "Formal Concept Analysis: Mathematical Foundations"
3. **Belohlavek** (2002): "Fuzzy Galois connections" and related fuzzy FCA work

## Contributing

Contributions are welcome! Areas for development:
- Additional semiring implementations
- Optimized lattice building algorithms
- More visualization options
- Jupyter notebook tutorials
- Unit tests

## License

MIT License (or specify your license)

## Contact

For questions or feedback, please open an issue on GitHub.

---

**Generated as part of a thesis on K-Formal Concept Analysis**
