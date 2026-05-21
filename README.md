
---

## Features

- Two-stage NEB workflow: endpoint minimization → NEB
- ML potential support (metatomic / PET-MAD models)
- Automatic structure preprocessing (wrapping, constraints, freezing)
- Simple CLI interface
- Python API for workflow integration (e.g., ChemReasoner)
- JSON-based configuration and outputs

---

## Installation

### 1. Prerequisites

#### eOn
Required backend engine:

```bash
conda install -c conda-forge eon
```

Or build from source:
https://github.com/TheochemUI/eOn

---

#### metatensor-tools (optional, for model conversion)

```bash
conda install -c conda-forge metatensor-tools
```

---

### 2. Install this package

```bash
git clone https://github.com/yourusername/eon-neb-runner.git
cd eon-neb-runner
pip install -e .
```

---

### 3. Verify installation

```bash
eon-neb-test
```

Checks:
- Python dependencies
- eOn executable
- CUDA availability
- ML backend support

---

## Models (IMPORTANT)

### Quick test mode (recommended)

A lightweight example model is included:

```
examples/models/pet-mad-xs.pt
```

This is sufficient to test the full NEB pipeline without installing
metatrain or downloading large checkpoints.

Example usage:

```bash
eon-neb reactant.con product.con \
  --model examples/models/pet-mad-xs.pt
```

---

### Full PET-MAD workflow (advanced)

To use production-quality PET-MAD models, export a checkpoint from Hugging Face:

```bash
mkdir -p models

mtt export \
  https://huggingface.co/lab-cosmo/upet/resolve/main/models/pet-mad-s-v1.5.0.ckpt \
  -o models/pet-mad-s-v1.5.0.pt
```

Then run:

```bash
eon-neb reactant.con product.con \
  --model models/pet-mad-s-v1.5.0.pt
```

> Note: Large model training and metatrain dependencies are not required
> for running this repository with the included example model.

---
## Known limitations

This implementation assumes **orthogonal simulation cells**.

Non-orthogonal cells may lead to incorrect interpolation, wrapping, and NEB forces, which can cause unstable or inaccurate reaction paths.

For best results, convert structures to an orthogonal supercell before running NEB.

---
## Quick Start

### CLI usage

```bash
# basic run
eon-neb reactant.con product.con --model examples/models/pet-mad-xs.pt

# custom settings
eon-neb reactant.con product.con \
  --model model.pt \
  --images 10 \
  --max-iter 5000 \
  --device cuda
```

---

### Using a config file

```bash
eon-neb reactant.con product.con --config neb_config.json
```

Generate template:

```bash
eon-neb --save-config template.json
```

---

## Python API

```python
from pathlib import Path
from eon_neb import NEBConfig, NEBRunner

config = NEBConfig(
    model_path=Path("examples/models/pet-mad-xs.pt"),
    n_images=8,
    max_iterations=3000,
    device="cuda"
)

runner = NEBRunner(config)

result = runner.run_from_files(
    Path("reactant.con"),
    Path("product.con"),
    workdir=Path("neb_run")
)

if result.success:
    print(f"Forward barrier: {result.forward_barrier:.3f} eV")
    print(f"Reaction energy: {result.reaction_energy:.3f} eV")
else:
    print(result.error_message)
```

---

## Configuration

### NEBConfig parameters

| Parameter | Default | Description |
|----------|--------|-------------|
| model_path | required | ML potential checkpoint |
| n_images | 8 | number of NEB images |
| max_iterations | 3000 | max optimization steps |
| device | cuda | cpu or cuda |

---

### Advanced JSON config

```json
{
  "model_path": "examples/models/pet-mad-xs.pt",
  "n_images": 8,
  "max_iterations": 3000,
  "device": "cuda",
  "neb_settings": {
    "spring": 4.0,
    "climbing_image_method": true,
    "ci_after": 0.2,
    "energy_weighted": true
  }
}
```

---

## Outputs

Each run generates:

- `reactant_min/` – reactant minimization outputs
- `product_min/` – product minimization outputs
- `reactant.con`, `product.con` – processed endpoints
- `neb.dat` – energy profile
- `summary.json` – results
- `neb.con` - final NEB trajectory
- `stdout.txt`, `stderr.txt` – logs

---

## Summary format

```json
{
  "success": true,
  "reaction_energy_eV": -0.234,
  "forward_barrier_eV": 0.856,
  "reverse_barrier_eV": 1.090,
  "ts_index": 5,
  "ts_energy_eV": -123.456
}
```


