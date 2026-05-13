# Single NEB: NO Dissociation on Ni(111) with Fe Substitution

A simple example of running a single NEB calculation with provided reactant and product structures.

## Quick Start

### Prerequisites

```bash
# Install the package
pip install -e /path/to/eon-neb-runner

# Have eOn installed and a trained ML potential model available
```

### Run the Calculation

```bash
cd examples/Single\ NEB\ -\ NO\ dissociation\ on\ Ni\(111\)\ with\ a\ Fe\ substitution

eon-neb reactant.con product.con --model /path/to/your/model.pt --images 8 --max-iter 3000
```

**Options:**
- `--model` (required): Path to ML potential checkpoint
- `--images`: Number of intermediate NEB images (default: 8)
- `--max-iter`: Maximum NEB iterations (default: 3000)
- `--device`: `cuda` or `cpu` (default: `cuda`)
- `--workdir`: Output directory for results (default: current directory)

### Python Usage

```python
from pathlib import Path
from eon_neb.config import NEBConfig
from eon_neb.runner import NEBRunner

config = NEBConfig(
    model_path=Path("/path/to/model.pt"),
    n_images=8,
    max_iterations=3000,
    device="cuda"
)

runner = NEBRunner(config)
result = runner.run_from_files(
    initial_file=Path("reactant.con"),
    final_file=Path("product.con"),
    workdir=Path("./neb_results")
)

print(f"Forward barrier: {result.forward_barrier:.3f} eV")
print(f"Reverse barrier: {result.reverse_barrier:.3f} eV")
print(f"Reaction energy: {result.reaction_energy:.3f} eV")
```

## Output

Results are saved to the working directory:

```
neb_results/
├── reactant_min/     # Minimized reactant endpoint
├── product_min/      # Minimized product endpoint
├── reactant.con      # NEB endpoint structure
├── product.con       # NEB endpoint structure
├── neb.dat          # NEB path data
├── summary.json     # Barriers and reaction energy
├── stdout.txt       # eOn output
└── stderr.txt       # eOn error log
```

## System Description

- **System**: Ni(111) surface with one Fe substitution
- **Adsorbate**: NO molecule
- **Reaction**: NO dissociation on the substituted surface
- **Structure**: eOn `.con` format (ASCII atomic configuration)

## Troubleshooting

- Check `stderr.txt` if the calculation fails
- Verify the model file path is correct
- Ensure eOn is properly installed: https://eondocs.org/team
