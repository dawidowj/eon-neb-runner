#!/usr/bin/env python
"""
Example: Running NEB with Python API

This shows how to use the eon-neb-runner package programmatically,
which is useful for integration into larger workflows like ChemReasoner.
"""

from pathlib import Path
from eon_neb import NEBConfig, NEBRunner

def main():
    # Method 1: Create config programmatically
    config = NEBConfig(
        model_path=Path("/nfs/hpc/share/dawidowj/bin/MLIP_checkpoints/pet-mad-s-v1.5.0.pt"),
        n_images=8,
        max_iterations=3000,
        device="cuda"
    )
    
    # Method 2: Load from JSON (recommended for reproducibility)
    # config = NEBConfig.from_json(Path("example_config.json"))
    
    # Initialize runner
    runner = NEBRunner(config)
    
    # Run NEB calculation
    result = runner.run_from_files(
        initial_file=Path("reactant.con"),
        final_file=Path("product.con"),
        workdir=Path("neb_output")
    )
    
    # Process results
    if result.success:
        print("\n✓ Calculation successful!")
        print(f"\nReaction energy: {result.reaction_energy:8.3f} eV")
        print(f"Forward barrier: {result.forward_barrier:8.3f} eV")
        print(f"Reverse barrier: {result.reverse_barrier:8.3f} eV")
        print(f"TS image:        {result.ts_index}")
        
        # Results are automatically saved to JSON
        print(f"\nResults saved to: {result.neb_path}/summary.json")
        
        # You can also access the result as a dictionary
        result_dict = result.to_dict()
        print("\nResult dictionary:")
        for key, value in result_dict.items():
            print(f"  {key}: {value}")
        
        return 0
    else:
        print("\n✗ Calculation failed!")
        print(f"Error: {result.error_message}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
