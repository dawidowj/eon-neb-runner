# Installation Guide

## For Users (Quick Install)

### Step 1: Set up eOn environment

If you already have an eOn conda environment (like the one in `eon_env.yml`):

```bash
conda activate eon  # or whatever your environment is called
```

If you need to create the environment from scratch:

```bash
conda env create -f eon_env.yml
conda activate eon
```

### Step 2: Install this package

```bash
cd /path/to/eon-neb-runner
pip install -e .
```

The `-e` flag installs in "editable" mode, so changes to the code are immediately available.

### Step 3: Verify installation

```bash
eon-neb-test
```

You should see:
```
✓ Python 3.10.x
✓ ASE x.xx.x
✓ NumPy x.xx.x
✓ rgpycrumbs available
✓ eonclient executable found
✓ CUDA available: [Your GPU]
✓ eon_neb package 0.1.0
```

### Step 4: Test with example

```bash
# Generate a config template
eon-neb --save-config my_config.json

# Edit my_config.json to point to your model
# Then run a calculation (you need reactant.con and product.con)
eon-neb reactant.con product.con --config my_config.json
```

## For Collaborators (From GitHub)

When the repository is hosted on GitHub:

```bash
# Clone the repository
git clone https://github.com/yourusername/eon-neb-runner.git
cd eon-neb-runner

# Make sure you're in your eOn conda environment
conda activate eon

# Install
pip install -e .

# Run tests
eon-neb-test
```

## For ChemReasoner Integration

If integrating into ChemReasoner:

```bash
cd /path/to/chemreasoner
git clone https://github.com/yourusername/eon-neb-runner.git tools/eon-neb-runner

# Install as part of chemreasoner environment
pip install -e tools/eon-neb-runner
```

Then in your ChemReasoner agents, you can:

```python
from eon_neb import NEBRunner, NEBConfig
```

## Troubleshooting

### Issue: "eonclient not found"

**Solution**: Make sure eOn is in your PATH
```bash
which eonclient  # Should show a path
conda activate eon  # Activate the environment with eOn
```

### Issue: "rgpycrumbs not installed"

**Solution**: Install it
```bash
pip install rgpycrumbs
```

### Issue: "Model not found"

**Solution**: Update the model path in your config:
```bash
# Check where your model is
ls /nfs/hpc/share/dawidowj/bin/MLIP_checkpoints/

# Update config.json with correct path
# Or use --model flag:
eon-neb reactant.con product.con --model /correct/path/to/model.pt
```

### Issue: CUDA out of memory

**Solution**: Use CPU instead
```bash
eon-neb reactant.con product.con --model model.pt --device cpu
```

## Development Installation

For development (if you want to modify the code):

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/eon-neb-runner.git
cd eon-neb-runner
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install

# Run tests
pytest tests/

# Format code
black eon_neb/
flake8 eon_neb/
```

## Verifying Your Installation

Create a simple test script:

```python
# test_install.py
from eon_neb import NEBConfig, NEBRunner
from pathlib import Path

print("✓ Package imported successfully")
print(f"✓ NEBRunner available")
print(f"✓ NEBConfig available")

# Try creating a config (will fail if model doesn't exist, but that's ok)
try:
    config = NEBConfig(model_path=Path("fake_model.pt"))
    print(f"✓ NEBConfig can be created")
except Exception as e:
    print(f"✗ Error: {e}")
```

Run it:
```bash
python test_install.py
```
