# NEB Batch from JSON Example

This example demonstrates how to run **multiple NEB calculations in batch mode** using a JSON input file with embedded pymatgen structures.

## Overview

Instead of running individual NEB calculations one at a time, you can package multiple initial-final structure pairs into a single JSON file and process them all at once using the `--json` flag.

## Structure of the JSON File

The `neb_batch.json` file contains an array of NEB jobs, each with:

- **`comment`**: A descriptive name for the calculation (used for output directory naming)
- **`initial`**: Initial structure in pymatgen `Structure.to_dict()` format
- **`final`**: Final structure in pymatgen `Structure.to_dict()` format
- **`metadata`** (optional): Additional information about the job
- **Freeze strategy options** (optional): Per-job overrides for atom freezing

Example structure:
```json
[
  {
    "comment": "CO_hop_Au",
    "initial": {
      "@module": "pymatgen.core.structure",
      "@class": "Structure",
      "lattice": {...},
      "sites": [...]
    },
    "final": {...},
    "freeze_strategy": "z",
    "freeze_z_max": 15.0
  }
]
```

## Running the Example

### Prerequisites

1. Install the package with all dependencies:
```bash
pip install -e /path/to/eon-neb-runner
```

2. Have a trained ML potential model available (`.pt` file)

3. Ensure `eonclient` is installed and available in your PATH

### Command Line Usage

Run the batch NEB calculations:

```bash
cd examples/NEB\ batch\ from\ json

eon-neb --json neb_batch.json --model /path/to/your/model.pt --images 8 --max-iter 3000
```

**Options:**
- `--json`: Path to the JSON batch file (required for batch mode)
- `--model`: Path to the ML potential checkpoint (required)
- `--images`: Number of intermediate NEB images (default: 8)
- `--max-iter`: Maximum NEB iterations (default: 3000)
- `--device`: Computing device: `cuda` or `cpu` (default: `cuda`)
- `--workdir`: Output directory for results (default: current directory)

### Python Usage

```python
from pathlib import Path
from eon_neb.config import NEBConfig
from eon_neb.runner import NEBRunner

# Create configuration
config = NEBConfig(
    model_path=Path("/path/to/model.pt"),
    n_images=8,
    max_iterations=3000,
    device="cuda"
)

# Run batch calculations
runner = NEBRunner(config)
results = runner.run_from_json(
    json_file=Path("neb_batch.json"),
    base_workdir=Path("./neb_results")
)

# Results are saved to neb_results/CO_hop_Au/, neb_results/..., etc.
```

## Output Structure

After running, results are organized as:

```
neb_results/
├── batch_summary.json          # Overall batch results
├── CO_hop_Au/
│   ├── reactant_min/           # Minimized reactant
│   │   └── min.con
│   ├── product_min/            # Minimized product
│   │   └── min.con
│   ├── reactant.con            # NEB endpoint
│   ├── product.con             # NEB endpoint
│   ├── neb.dat                 # NEB path data
│   ├── summary.json            # NEB results (barriers, reaction energy)
│   ├── stdout.txt              # eOn output log
│   └── stderr.txt              # eOn error log
├── [next_job_name]/
│   └── ...
```

## JSON File Format Details

The JSON file uses pymatgen's Structure format with `MontyEncoder`/`MontyDecoder` for serialization. This format includes:

- **Lattice information**: Cell parameters, PBC conditions
- **Atomic sites**: Symbols, positions (both fractional and Cartesian)
- **Optional properties**: Selective dynamics, tags, other metadata

For details on how to generate JSON files from structure files, see the [pymatgen documentation](https://pymatgen.org/pymatgen.core.html#pymatgen.core.structure.Structure).

## Creating Your Own JSON Batch File

### From ASE/VASP files:

```python
from pathlib import Path
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.json import MontyEncoder
import json

# Read structures
initial_atoms = read("POSCAR_initial")  # ASE read
final_atoms = read("POSCAR_final")

# Convert to pymatgen
initial_struct = AseAtomsAdaptor.get_structure(initial_atoms)
final_struct = AseAtomsAdaptor.get_structure(final_atoms)

# Create job entry
job = {
    "comment": "my_reaction",
    "initial": initial_struct.to_dict(),
    "final": final_struct.to_dict(),
}

# Save as JSON
jobs = [job]
with open("my_batch.json", "w") as f:
    json.dump(jobs, f, cls=MontyEncoder, indent=2)
```

### From pymatgen Structure objects directly:

```python
from pymatgen.core import Structure
import json
from pymatgen.io.json import MontyEncoder

structures = [Structure.from_file("file1.cif"), Structure.from_file("file2.cif")]

jobs = [
    {
        "comment": f"job_{i}",
        "initial": structures[i].to_dict(),
        "final": structures[i+1].to_dict(),
    }
    for i in range(len(structures) - 1)
]

with open("batch.json", "w") as f:
    json.dump(jobs, f, cls=MontyEncoder, indent=2)
```

## Troubleshooting

**Q: JSON parsing fails with `MontyDecoder` errors**
- A: Make sure pymatgen is installed: `pip install pymatgen>=2024.1.1`

**Q: `eonclient` not found**
- A: Install eOn following the [eOn documentation](https://eondocs.org/team)

**Q: Results directories are empty**
- A: Check `stderr.txt` in each job directory for eOn error messages

**Q: Wrong freeze atoms in NEB**
- A: You can override freeze settings per job in the JSON file or use global `--freeze-strategy` CLI flag

## See Also

- [Main README](../../README.md) for general usage
- [eOn Documentation](https://eondocs.org/team) for detailed eOn configuration
- [pymatgen Structure Documentation](https://pymatgen.org/pymatgen.core.html#pymatgen.core.structure.Structure)
