# eOn NEB Runner with ML Potentials

A Python package for running Nudged Elastic Band (NEB) calculations using [eOn](https://theory.cm.utexas.edu/eon/) with machine learning potentials (MLIPs).

## Features

- **Two-stage NEB workflow**: Endpoint minimization → NEB calculation
- **ML potential support**: Uses metatomic/PET-MAD models via eOn
- **Automatic preprocessing**: Handles structure wrapping, constraint freezing
- **Simple CLI**: Easy command-line interface
- **Python API**: Integrate into larger workflows (e.g., ChemReasoner)
- **JSON I/O**: Configuration and results in JSON format

## Installation

### Prerequisites

1. **eOn**: Must be installed and available in your environment
   - Install via conda: `conda install -c conda-forge eon`
   - Or build from source: https://github.com/TheochemUI/eOn

2. **ML Model**: You need a trained model checkpoint (e.g., PET-MAD-S)

### Install from source

```bash
git clone https://github.com/yourusername/eon-neb-runner.git
cd eon-neb-runner
pip install -e .
```

### Verify installation

```bash
eon-neb-test
```

This will check:
- Python version
- Required packages (ASE, NumPy, rgpycrumbs)
- eOn executable
- CUDA availability (if applicable)

## Quick Start

### Command Line

```bash
# Basic usage
eon-neb reactant.con product.con --model /path/to/model.pt

# With custom settings
eon-neb reactant.con product.con \
  --model model.pt \
  --images 10 \
  --max-iter 5000 \
  --device cuda

# Using a configuration file
eon-neb reactant.con product.con --config neb_config.json

# Generate a config template
eon-neb --save-config template.json
```

### Python API

```python
from pathlib import Path
from eon_neb import NEBConfig, NEBRunner

# Create configuration
config = NEBConfig(
    model_path=Path("/path/to/model.pt"),
    n_images=8,
    max_iterations=3000,
    device="cuda"
)

# Run NEB
runner = NEBRunner(config)
result = runner.run_from_files(
    Path("reactant.con"),
    Path("product.con"),
    workdir=Path("neb_calculation")
)

# Check results
if result.success:
    print(f"Forward barrier: {result.forward_barrier:.3f} eV")
    print(f"Reaction energy: {result.reaction_energy:.3f} eV")
else:
    print(f"Failed: {result.error_message}")
```

### JSON Interface (for ChemReasoner integration)

```python
import json
from pathlib import Path
from eon_neb import NEBConfig, NEBRunner
from ase.io import read

# Load configuration from JSON
config = NEBConfig.from_json(Path("neb_config.json"))

# Run calculation
runner = NEBRunner(config)

# Load structures from JSON-specified paths
with open("pathway_spec.json") as f:
    pathway = json.load(f)

initial = read(pathway["reactant_structure"])
final = read(pathway["product_structure"])

result = runner.run_neb(initial, final, Path("output"))

# Save results to JSON
result.to_json(Path("output/neb_results.json"))
```

## Configuration

### NEBConfig Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `model_path` | Required | Path to ML potential checkpoint |
| `n_images` | 8 | Number of intermediate NEB images |
| `max_iterations` | 3000 | Maximum NEB iterations |
| `device` | "cuda" | Device for calculations ("cuda" or "cpu") |
| `metals` | See code | Set of metal symbols to freeze |

### Advanced Settings

See `NEBConfig` class for:
- `endpoint_min_settings`: Control endpoint minimization
- `neb_settings`: Spring constants, climbing image, energy weighting

Example JSON configuration:

```json
{
  "model_path": "/path/to/model.pt",
  "n_images": 8,
  "max_iterations": 3000,
  "device": "cuda",
  "metals": ["Pt", "Fe", "Ce"],
  "neb_settings": {
    "spring": 4.0,
    "climbing_image_method": true,
    "ci_after": 0.2,
    "energy_weighted": true,
    "ew_ksp_min": 0.99,
    "ew_ksp_max": 2.59
  }
}
```

## Output

Each NEB calculation produces:

- `reactant_min/`: Minimized reactant structure
- `product_min/`: Minimized product structure  
- `reactant.con`, `product.con`: Preprocessed endpoints
- `neb.dat`: Energy profile along reaction coordinate
- `config.ini`: eOn configuration used
- `summary.json`: Results in JSON format
- `stdout.txt`, `stderr.txt`: Calculation logs

### summary.json Format

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

## Examples

See `examples/` directory for:
- Simple diffusion barriers
- Surface reaction pathways
- CO2 reduction on CeFe oxide (coming soon with Pragya's structures)

## For ChemReasoner Integration

This package is designed to be used as an agent within the [ChemReasoner](https://github.com/pnnl/chemreasoner) framework:

1. **Input**: JSON file specifying reactant/product structures and calculation parameters
2. **Processing**: Automated NEB calculation with ML potential
3. **Output**: JSON file with barrier heights and reaction energies

See `examples/chemreasoner_agent/` for integration templates (TODO).

## Troubleshooting

### eonclient not found

Ensure eOn is installed and activated:
```bash
conda activate your-eon-environment
which eonclient  # Should show path to executable
```

### CUDA errors

If CUDA is unavailable, use CPU:
```bash
eon-neb reactant.con product.con --model model.pt --device cpu
```

### Model not found

Verify model path:
```bash
ls -lh /path/to/model.pt
```

## Development

### Running tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Code formatting

```bash
black eon_neb/
flake8 eon_neb/
```

## Citation

If you use this code, please cite:

## License
## Contributing
## Contact
## Acknowledgments
