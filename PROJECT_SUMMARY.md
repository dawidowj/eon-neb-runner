# eOn NEB Runner - Project Summary

**Purpose**: NEB agent for ChemReasoner project (CO2 reduction on CeFe oxide)

## What This Is

A Python package that wraps eOn + PET-MAD NEB workflow into a reusable tool that:
1. Can be easily installed (`pip install -e .`)
2. Has a simple command-line interface
3. Provides a Python API for programmatic use
4. Outputs results in JSON format (ready for ChemReasoner integration)
5. Includes tests to verify installation

## Quick Start

```bash
# 1. Get the code
git clone https://github.com/dawidowj/eon-neb-runner.git
cd eon-neb-runner

# 2. Install (in your eOn conda environment)
conda activate eon
pip install -e .

# 3. Set up default model
eon-neb-setup

# 4. Test installation
eon-neb-test

# 5. Run a calculation
eon-neb reactant.con product.con
```

## Files Overview

```
eon-neb-runner/
├── README.md              # Main documentation
├── INSTALL.md             # Installation guide
├── setup.py               # Package installer
├── requirements.txt       # Python dependencies
│
├── eon_neb/               # Main package code
│   ├── __init__.py        # Package exports
│   ├── config.py          # Configuration management (NEBConfig)
│   ├── runner.py          # Core NEB logic (NEBRunner)
│   ├── cli.py             # Command-line interface
│   ├── setup_config.py    # Interactive setup tool
│   └── tests/             # Test suite
│       └── test_installation.py
│
└── examples/              # Usage examples
    ├── example_config.json
    └── run_neb_example.py
```

## Usage Modes

### 1. Command Line (Simplest)

```bash
eon-neb initial.con final.con
```

### 2. With Config File (Recommended for reproducibility)

```bash
# Save a template
eon-neb --save-config my_settings.json

# Edit my_settings.json, then run
eon-neb initial.con final.con --config my_settings.json
```

### 3. Python API (For ChemReasoner)

```python
from eon_neb import NEBConfig, NEBRunner
from pathlib import Path

config = NEBConfig.from_json(Path("config.json"))
runner = NEBRunner(config)
result = runner.run_from_files(
    Path("reactant.con"),
    Path("product.con"),
    workdir=Path("output")
)

if result.success:
    print(f"Barrier: {result.forward_barrier} eV")
    result.to_json(Path("output/results.json"))
```

## Output Format

Every calculation produces a `summary.json`:

```json
{
  "success": true,
  "reaction_energy_eV": -0.234,
  "forward_barrier_eV": 0.856,
  "reverse_barrier_eV": 1.090,
  "ts_index": 5,
  "ts_energy_eV": -123.456,
  "neb_path": "/path/to/calculation"
}
```

This format is ready to be consumed by ChemReasoner or other automation tools.
