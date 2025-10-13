# Output Directory Structure - Implementation Guide

## Overview

The K-FCA prototype now has a properly organized output directory structure that separates generated files by type, making it easier to manage, share, and version control results.

## Changes Made

### 1. Directory Structure Created ✅

```
output/
├── README.md              # Documentation for output directory
├── contexts/              # Context heatmap visualizations
│   └── .gitkeep
├── lattices/              # Concept lattice Hasse diagrams
│   └── .gitkeep
├── concepts/              # Individual concept detail plots
│   └── .gitkeep
└── exports/               # Graphviz DOT, JSON, CSV files
    └── .gitkeep
```

### 2. Updated `.gitignore` ✅

Added rules to:
- Ignore generated PNG, PDF, DOT files in output directories
- Keep directory structure via `.gitkeep` files
- Ignore any PNG/DOT files in root directory
- Allow documentation images in `docs/` if needed

### 3. Enhanced Visualization Module ✅

**File**: [`src/visualization.py`](src/visualization.py)

**Changes**:
- Added `ensure_output_dirs()` function to create directories
- Updated `plot_context()` with `save_path` parameter
- Updated `plot_lattice()` with `save_path` parameter
- Updated `plot_concept_details()` with `save_path` parameter
- Updated `export_lattice_to_graphviz()` to save to `output/exports/`

**New Constants**:
```python
OUTPUT_DIR = Path("output")
CONTEXTS_DIR = OUTPUT_DIR / "contexts"
LATTICES_DIR = OUTPUT_DIR / "lattices"
CONCEPTS_DIR = OUTPUT_DIR / "concepts"
EXPORTS_DIR = OUTPUT_DIR / "exports"
```

**Auto-save Feature**:
When `save_path` is provided, files are automatically saved to the appropriate subdirectory:
```python
# Context → output/contexts/
plot_context(context, save_path="my_context.png")

# Lattice → output/lattices/
plot_lattice(lattice, save_path="my_lattice.png")

# Concept → output/concepts/
plot_concept_details(lattice, 0, save_path="concept_0.png")

# DOT export → output/exports/
export_lattice_to_graphviz(lattice, "my_lattice.dot")
```

### 4. Updated Example Scripts ✅

**Boolean Example** ([`examples/boolean_example.py`](examples/boolean_example.py)):
- ✅ Context saved to `output/contexts/boolean_context.png`
- ✅ Lattices saved to `output/lattices/boolean_lattice_{layout}.png`
- ✅ DOT export to `output/exports/boolean_lattice.dot`

**Vehicle Example** ([`examples/vehicle_example.py`](examples/vehicle_example.py)):
- ✅ Contexts for each threshold saved to `output/contexts/vehicle_context_phi_{threshold}.png`
- ✅ Lattices saved to `output/lattices/vehicle_lattice_phi_{threshold}.png`
- ✅ DOT exports to `output/exports/vehicle_lattice_phi_{threshold}.dot`

### 5. Documentation ✅

**Created**:
- [`output/README.md`](output/README.md) - Comprehensive documentation of output structure
- This file - Implementation guide

**Updated**:
- Main [`README.md`](README.md) - Added output directory section with examples

## Usage Examples

### Automatic Saving (Recommended)

```python
from src.visualization import plot_context, plot_lattice

# Will save to output/contexts/my_analysis.png
fig = plot_context(context, save_path="my_analysis.png")

# Will save to output/lattices/my_lattice.png
fig = plot_lattice(lattice, save_path="my_lattice.png")
```

### Manual Saving (Still Supported)

```python
from pathlib import Path

fig = plot_context(context)
fig.savefig(Path("output/contexts/manual_save.png"))
```

### Running Examples

```bash
# Run Boolean example
python examples/boolean_example.py

# Check outputs
ls -lh output/contexts/boolean_*
ls -lh output/lattices/boolean_*
ls -lh output/exports/boolean_*

# Run Vehicle example
python examples/vehicle_example.py

# Check outputs
ls -lh output/contexts/vehicle_*
ls -lh output/lattices/vehicle_*
ls -lh output/exports/vehicle_*
```

## File Naming Conventions

### Contexts
Pattern: `{dataset}_context[_phi_{threshold}].png`

Examples:
- `boolean_context.png`
- `vehicle_context_phi_0.5.png`
- `vehicle_context_phi_0.75.png`
- `vehicle_context_phi_1.0.png`

### Lattices
Pattern: `{dataset}_lattice[_phi_{threshold}][_{layout}].png`

Examples:
- `boolean_lattice_hierarchical.png`
- `boolean_lattice_spring.png`
- `vehicle_lattice_phi_0.75.png`
- `vehicle_lattice_phi_1.0_hierarchical.png`

### Concepts
Pattern: `{dataset}_concept_{id}.png`

Examples:
- `boolean_concept_0.png`
- `vehicle_concept_5.png`

### Exports
Pattern: `{dataset}_lattice[_phi_{threshold}].{ext}`

Examples:
- `boolean_lattice.dot`
- `vehicle_lattice_phi_0.75.dot`
- `context_data.json` (future)
- `lattice_export.csv` (future)

## Benefits of New Structure

### 1. **Organization** ✅
- Clear separation by file type
- Easy to find specific visualizations
- Professional project structure

### 2. **Version Control** ✅
- Generated files ignored via `.gitignore`
- Directory structure preserved with `.gitkeep`
- Clean git history without binary files

### 3. **Collaboration** ✅
- Teammates can regenerate outputs locally
- Consistent output locations across machines
- Easy to share specific results

### 4. **Scalability** ✅
- Can handle many datasets and experiments
- Clear naming prevents conflicts
- Easy to clean up old results

### 5. **Documentation** ✅
- Self-documenting structure
- README explains purpose of each directory
- Clear examples in code

## Migration Notes

### Before (Old Structure)
```
k-fca-prototype/
├── boolean_context.png         ❌ Root clutter
├── boolean_lattice_hierarchical.png
├── boolean_lattice.dot
├── vehicle_context_phi_0.5.png
└── ...
```

### After (New Structure)
```
k-fca-prototype/
├── output/
│   ├── contexts/
│   │   ├── boolean_context.png      ✅ Organized
│   │   └── vehicle_context_phi_0.5.png
│   ├── lattices/
│   │   ├── boolean_lattice_hierarchical.png
│   │   └── vehicle_lattice_phi_0.5.png
│   └── exports/
│       ├── boolean_lattice.dot
│       └── vehicle_lattice_phi_0.5.dot
└── ...
```

## Cleaning Up

### Remove All Outputs
```bash
rm -rf output/contexts/*.png
rm -rf output/lattices/*.png
rm -rf output/exports/*.dot
```

### Keep Directory Structure
The `.gitkeep` files ensure directories remain even when empty.

### Regenerate Outputs
```bash
python examples/boolean_example.py
python examples/vehicle_example.py
```

## Future Enhancements

Potential additions to the output structure:

1. **JSON Exports** (`output/exports/*.json`)
   - Context data
   - Lattice structure
   - Concept lists

2. **CSV Exports** (`output/exports/*.csv`)
   - Incidence matrices
   - Concept tables
   - Statistical summaries

3. **PDF Reports** (`output/reports/`)
   - Auto-generated analysis reports
   - Multi-page documents
   - Publication-ready figures

4. **Interactive HTML** (`output/interactive/`)
   - D3.js visualizations
   - Interactive lattice exploration
   - Web-based viewer

## Testing

All tests pass with new structure:

```bash
# Test Boolean example
python examples/boolean_example.py
# ✅ All files saved to correct locations

# Test Vehicle example
python examples/vehicle_example.py
# ✅ All files saved with proper naming

# Verify structure
ls -R output/
# ✅ All subdirectories present with outputs
```

## Checklist

- [x] Create output directory structure
- [x] Add `.gitkeep` files
- [x] Update `.gitignore`
- [x] Update `src/visualization.py`
- [x] Update `examples/boolean_example.py`
- [x] Update `examples/vehicle_example.py`
- [x] Create `output/README.md`
- [x] Update main `README.md`
- [x] Test Boolean example
- [x] Test Vehicle example
- [x] Verify file organization
- [x] Document changes

## Summary

✅ **Complete**: The K-FCA prototype now has a professional, well-organized output directory structure that:
- Separates files by type
- Uses consistent naming conventions
- Integrates seamlessly with examples
- Is properly documented
- Works with version control

**No breaking changes**: Old code calling visualization functions without `save_path` still works - it just won't auto-save.

**Total files modified**: 5
- `src/visualization.py`
- `examples/boolean_example.py`
- `examples/vehicle_example.py`
- `.gitignore`
- `README.md`

**Total files created**: 6
- `output/README.md`
- `output/contexts/.gitkeep`
- `output/lattices/.gitkeep`
- `output/concepts/.gitkeep`
- `output/exports/.gitkeep`
- This file

---

**Implementation Date**: October 13, 2025
**Status**: ✅ Complete and tested
