# eOn NEB Runner - Project Summary

**Author**: [Your name]  
**Date**: 2025  
**Purpose**: NEB agent for ChemReasoner project (CO2 reduction on CeFe oxide)

## What This Is

A Python package that wraps your eOn + PET-MAD NEB workflow into a reusable tool that:
1. Can be easily installed by collaborators (`pip install -e .`)
2. Has a simple command-line interface
3. Provides a Python API for programmatic use
4. Outputs results in JSON format (ready for ChemReasoner integration)
5. Includes tests to verify installation

## Quick Start for Collaborators

```bash
# 1. Get the code (once it's in a repo)
git clone [repo-url]
cd eon-neb-runner

# 2. Install (in your eOn conda environment)
conda activate eon
pip install -e .

# 3. Test installation
eon-neb-test

# 4. Run a calculation
eon-neb reactant.con product.con --model /path/to/model.pt
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
│   └── cli.py             # Command-line interface
│
├── tests/                 # Installation tests
│   ├── __init__.py
│   └── test_installation.py
│
└── examples/              # Usage examples
    ├── example_config.json
    └── run_neb_example.py
```

## Usage Modes

### 1. Command Line (Simplest)

```bash
eon-neb initial.con final.con --model model.pt
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

## What's Next (Your Milestones)

Based on the email, here's what you need to do:

### ✓ Done:
- [x] Basic NEB runner with eOn + ML potential
- [x] Packaged code with `setup.py`
- [x] Installation tests (`eon-neb-test`)
- [x] Command-line interface
- [x] Python API
- [x] JSON input/output support

### 🔄 In Progress:
- [ ] Share with Pragya (get access to repo)
- [ ] Pragya provides CeFe oxide structures
- [ ] Test on real CO2 reduction pathways

### 📋 TODO:
- [ ] Extend to handle pathway directories (batch processing)
- [ ] Add more error recovery
- [ ] Integration examples for ChemReasoner
- [ ] Documentation for paper

## Sharing with Team

### Option 1: Internal PNNL Repo
Pragya has access - ask your PI to add this there.

### Option 2: External GitHub Repo
Your PI mentioned having an external repo. Clone this there:

```bash
cd /path/to/external-repo
git add eon-neb-runner/
git commit -m "Add NEB runner package"
git push
```

### Option 3: Direct Share (Temporary)
Zip and email:

```bash
cd eon-neb-runner
tar -czf eon-neb-runner.tar.gz .
# Email eon-neb-runner.tar.gz to collaborators
```

They unzip and run:
```bash
tar -xzf eon-neb-runner.tar.gz
cd eon-neb-runner
pip install -e .
```

## Testing Checklist

Before sharing, verify:

- [ ] `eon-neb-test` passes
- [ ] Can run on a simple example
- [ ] README is clear
- [ ] INSTALL.md covers common issues
- [ ] Example config works

## Questions for Your PI / Team

1. **Repo location**: Internal PNNL or external GitHub?
2. **Model distribution**: Can collaborators access PET-MAD-S model?
3. **Computing resources**: Who has GPU access?
4. **ChemReasoner integration**: Timeline for integration?
5. **Paper authorship**: Who's contributing what?

## Notes for Pragya

When you provide the 3D structures for CO2 reduction pathways:

1. Save each pathway as: `pathway_N/reactant.con` and `pathway_N/product.con`
2. Or provide a JSON manifest:

```json
{
  "pathways": [
    {
      "name": "CO2_to_CO",
      "reactant": "structures/co2_adsorbed.con",
      "product": "structures/co_plus_o.con"
    },
    {
      "name": "CO_to_C",
      "reactant": "structures/co_adsorbed.con", 
      "product": "structures/c_plus_o.con"
    }
  ]
}
```

Then we can batch process them all!

## Contact

[Your email/Slack/etc.]

## Acknowledgments

- PNNL ChemReasoner team
- eOn developers
- PET-MAD model authors
