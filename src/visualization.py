"""
Visualization utilities for K-FCA

Provides functions to visualize:
- K-valued formal contexts as heatmaps
- Concept lattices as Hasse diagrams
- Individual concepts with their extent and intent

Output directory structure:
- output/contexts/  : Context heatmaps
- output/lattices/  : Concept lattice diagrams
- output/concepts/  : Individual concept details
- output/exports/   : Graphviz DOT files, JSON, CSV
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import networkx as nx
from typing import Optional, Dict, Tuple, List
from pathlib import Path
from .context import KValuedContext
from .lattice import ConceptLattice


# Output directory paths
OUTPUT_DIR = Path("output")
CONTEXTS_DIR = OUTPUT_DIR / "contexts"
LATTICES_DIR = OUTPUT_DIR / "lattices"
CONCEPTS_DIR = OUTPUT_DIR / "concepts"
EXPORTS_DIR = OUTPUT_DIR / "exports"


def ensure_output_dirs():
    """Create output directories if they don't exist."""
    for dir_path in [CONTEXTS_DIR, LATTICES_DIR, CONCEPTS_DIR, EXPORTS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def plot_context(
    context: KValuedContext,
    figsize: Tuple[int, int] = (10, 8),
    cmap: str = "YlOrRd",
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot K-valued context as a heatmap.

    Args:
        context: The K-valued formal context
        figsize: Figure size (width, height)
        cmap: Colormap name
        title: Plot title
        save_path: Optional path to save figure (relative to output/contexts/)
                  If None, doesn't save automatically

    Returns:
        Matplotlib figure
    """
    ensure_output_dirs()
    fig, ax = plt.subplots(figsize=figsize)

    # Convert relation to float for plotting
    data = np.zeros(context.relation.shape)
    for i in range(context.relation.shape[0]):
        for j in range(context.relation.shape[1]):
            val = context.relation[i, j]
            if isinstance(val, (int, float)):
                data[i, j] = float(val)
            else:
                data[i, j] = 0  # For non-numeric semiring values

    # Create heatmap
    im = ax.imshow(data, cmap=cmap, aspect='auto', interpolation='nearest')

    # Set ticks and labels
    ax.set_xticks(np.arange(len(context.attributes)))
    ax.set_yticks(np.arange(len(context.objects)))
    ax.set_xticklabels(context.attributes)
    ax.set_yticklabels(context.objects)

    # Rotate attribute labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add values in cells
    for i in range(len(context.objects)):
        for j in range(len(context.attributes)):
            val = context.relation[i, j]
            text = ax.text(j, i, str(val), ha="center", va="center",
                          color="black" if data[i, j] < 0.5 else "white",
                          fontsize=9)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Incidence Degree', rotation=270, labelpad=15)

    # Title
    if title is None:
        title = f"K-Valued Formal Context\n{context.semiring}"
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Labels
    ax.set_xlabel('Attributes', fontsize=12)
    ax.set_ylabel('Objects', fontsize=12)

    plt.tight_layout()

    # Auto-save if path provided
    if save_path:
        full_path = CONTEXTS_DIR / save_path
        fig.savefig(full_path, dpi=150, bbox_inches='tight')

    return fig


def plot_lattice(
    lattice: ConceptLattice,
    figsize: Tuple[int, int] = (14, 10),
    layout: str = "hierarchical",
    show_labels: bool = True,
    node_size: int = 1200,
    font_size: int = 8,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot concept lattice as a Hasse diagram.

    Args:
        lattice: The concept lattice
        figsize: Figure size (width, height)
        layout: Layout algorithm ('hierarchical', 'spring', 'circular')
        show_labels: Whether to show concept labels
        node_size: Size of concept nodes
        font_size: Font size for labels
        title: Plot title
        save_path: Optional path to save figure (relative to output/lattices/)

    Returns:
        Matplotlib figure
    """
    ensure_output_dirs()
    fig, ax = plt.subplots(figsize=figsize)

    # Create directed graph
    G = nx.DiGraph()

    # Add nodes (concepts)
    for i in range(len(lattice.concepts)):
        G.add_node(i)

    # Add edges (cover relation from Hasse diagram)
    for i in range(len(lattice.concepts)):
        for j in lattice.upper_neighbors[i]:
            G.add_edge(i, j)

    # Compute layout
    if layout == "hierarchical":
        pos = _hierarchical_layout(G, lattice)
    elif layout == "spring":
        pos = nx.spring_layout(G, k=2, iterations=50)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    else:
        pos = nx.kamada_kawai_layout(G)

    # Draw edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color='gray',
        arrows=True,
        arrowsize=15,
        arrowstyle='-|>',
        width=1.5,
        alpha=0.6
    )

    # Draw nodes
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color='lightblue',
        node_size=node_size,
        edgecolors='darkblue',
        linewidths=2
    )

    # Draw labels
    if show_labels:
        labels = {}
        for i in range(len(lattice.concepts)):
            concept = lattice.concepts[i]
            objs = lattice.get_concept_objects(i)
            attrs = lattice.get_concept_attributes(i)

            # Format label
            obj_str = ', '.join(objs[:3])
            if len(objs) > 3:
                obj_str += f", +{len(objs)-3}"

            attr_str = ', '.join(attrs[:3])
            if len(attrs) > 3:
                attr_str += f", +{len(attrs)-3}"

            labels[i] = f"{i}\n({obj_str})\n[{attr_str}]"

        nx.draw_networkx_labels(
            G, pos, labels, ax=ax,
            font_size=font_size,
            font_color='black',
            font_weight='normal'
        )

    # Title
    if title is None:
        title = f"φ-Concept Lattice\n{len(lattice)} concepts, pivot={lattice.galois.pivot}"
    ax.set_title(title, fontsize=14, fontweight='bold')

    ax.axis('off')
    plt.tight_layout()

    # Auto-save if path provided
    if save_path:
        full_path = LATTICES_DIR / save_path
        fig.savefig(full_path, dpi=150, bbox_inches='tight')

    return fig


def _hierarchical_layout(G: nx.DiGraph, lattice: ConceptLattice) -> Dict[int, Tuple[float, float]]:
    """
    Compute hierarchical layout for lattice based on concept sizes.

    Args:
        G: NetworkX graph
        lattice: Concept lattice

    Returns:
        Dictionary mapping node IDs to (x, y) positions
    """
    pos = {}
    n_concepts = len(lattice.concepts)

    # Group concepts by extent size (level in hierarchy)
    levels: Dict[int, List[int]] = {}
    for i in range(n_concepts):
        size = len(lattice.concepts[i].extent_idx)
        if size not in levels:
            levels[size] = []
        levels[size].append(i)

    # Assign positions
    sorted_levels = sorted(levels.keys(), reverse=True)  # Top to bottom
    max_width = max(len(levels[level]) for level in sorted_levels)

    for level_idx, size in enumerate(sorted_levels):
        concepts = levels[size]
        y = level_idx / (len(sorted_levels) - 1) if len(sorted_levels) > 1 else 0.5

        # Distribute horizontally
        for i, concept_id in enumerate(concepts):
            x = (i + 1) / (len(concepts) + 1) if len(concepts) > 1 else 0.5
            pos[concept_id] = (x, 1 - y)  # Flip y for top-down

    return pos


def plot_concept_details(
    lattice: ConceptLattice,
    concept_id: int,
    figsize: Tuple[int, int] = (10, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plot detailed view of a single concept.

    Args:
        lattice: The concept lattice
        concept_id: ID of concept to display
        figsize: Figure size
        save_path: Optional path to save figure (relative to output/concepts/)

    Returns:
        Matplotlib figure
    """
    ensure_output_dirs()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    concept = lattice.concepts[concept_id]
    objects = lattice.get_concept_objects(concept_id)
    attributes = lattice.get_concept_attributes(concept_id)

    # Plot extent
    ax1.barh(range(len(objects)), [1] * len(objects), color='steelblue')
    ax1.set_yticks(range(len(objects)))
    ax1.set_yticklabels(objects)
    ax1.set_xlabel('Membership')
    ax1.set_title(f'Extent (Objects)', fontweight='bold')
    ax1.set_xlim(0, 1.2)
    ax1.invert_yaxis()

    # Plot intent
    ax2.barh(range(len(attributes)), [1] * len(attributes), color='coral')
    ax2.set_yticks(range(len(attributes)))
    ax2.set_yticklabels(attributes)
    ax2.set_xlabel('Membership')
    ax2.set_title(f'Intent (Attributes)', fontweight='bold')
    ax2.set_xlim(0, 1.2)
    ax2.invert_yaxis()

    fig.suptitle(f'Concept #{concept_id}', fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Auto-save if path provided
    if save_path:
        full_path = CONCEPTS_DIR / save_path
        fig.savefig(full_path, dpi=150, bbox_inches='tight')

    return fig


def export_lattice_to_graphviz(
    lattice: ConceptLattice,
    filename: str = "lattice.dot"
) -> str:
    """
    Export lattice to Graphviz DOT format.

    Args:
        lattice: The concept lattice
        filename: Output filename (saved to output/exports/)

    Returns:
        Full path to saved file
    """
    ensure_output_dirs()

    lines = ["digraph ConceptLattice {"]
    lines.append("    rankdir=BT;")  # Bottom to top
    lines.append("    node [shape=box, style=rounded];")

    # Add nodes
    for i in range(len(lattice.concepts)):
        objs = lattice.get_concept_objects(i)
        attrs = lattice.get_concept_attributes(i)

        label = f"{i}\\n({', '.join(objs)})\\n[{', '.join(attrs)}]"
        lines.append(f'    {i} [label="{label}"];')

    # Add edges
    for i in range(len(lattice.concepts)):
        for j in lattice.upper_neighbors[i]:
            lines.append(f"    {i} -> {j};")

    lines.append("}")

    # Save to exports directory
    full_path = EXPORTS_DIR / filename
    with open(full_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"✓ Lattice exported to {full_path}")
    return str(full_path)
