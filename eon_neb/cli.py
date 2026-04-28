#!/usr/bin/env python
"""Command-line interface for eOn NEB runner."""

import argparse
from pathlib import Path
import sys

from .config import NEBConfig
from .runner import NEBRunner


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run NEB calculations with eOn and ML potentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  eon-neb reactant.con product.con --model /path/to/model.pt
  
  # With custom settings
  eon-neb reactant.con product.con --model model.pt --images 10 --device cpu
  
  # Using config file
  eon-neb reactant.con product.con --config neb_config.json
  
  # Save config template
  eon-neb --save-config template.json
        """
    )
    
    parser.add_argument(
        "initial",
        nargs="?",
        type=Path,
        help="Initial structure file (reactant)"
    )
    
    parser.add_argument(
        "final",
        nargs="?",
        type=Path,
        help="Final structure file (product)"
    )
    
    parser.add_argument(
        "--model",
        type=Path,
        help="Path to ML potential checkpoint (.pt file)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON configuration file"
    )
    
    parser.add_argument(
        "--images",
        type=int,
        default=8,
        help="Number of intermediate NEB images (default: 8)"
    )
    
    parser.add_argument(
        "--max-iter",
        type=int,
        default=3000,
        help="Maximum NEB iterations (default: 3000)"
    )
    
    parser.add_argument(
        "--device",
        choices=["cuda", "cpu"],
        default="cuda",
        help="Computing device (default: cuda)"
    )
    
    parser.add_argument(
        "--workdir",
        type=Path,
        help="Working directory for NEB calculation (default: current directory)"
    )
    
    parser.add_argument(
        "--save-config",
        type=Path,
        metavar="FILE",
        help="Save a template configuration file and exit"
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="JSON file with multiple NEB inputs"
    )
    parser.add_argument(
        "--freeze-strategy",
        choices=["element", "exclude_indices", "index", "z", "layers"],
        help="Atom freezing strategy"
    )

    parser.add_argument(
        "--freeze-indices",
        type=int,
        nargs="*",
        help="List of atom indices to freeze (for index strategy)"
    )

    parser.add_argument(
        "--freeze-z-max",
        type=float,
        help="Freeze atoms below this z value (for z strategy)"
    )

    parser.add_argument(
        "--freeze-n-layers",
        type=int,
        help="Number of bottom layers to freeze (for layers strategy)"
    )
    parser.add_argument("--freeze-elements", nargs="+", help="Atomic symbols of elemenets to freeze (for elements strategy)")
    
    # --- Minimization ---
    parser.add_argument("--min-freeze-strategy", choices=["none","index","element","z","layers"])
    parser.add_argument("--min-freeze-indices", nargs="+", type=int)
    parser.add_argument("--min-freeze-elements", nargs="+")
    parser.add_argument("--min-freeze-z-max", type=float)
    parser.add_argument("--min-freeze-n-layers", type=int)
    
    # --- NEB ---
    parser.add_argument("--neb-freeze-strategy", choices=["none","index","element","z","layers"])
    parser.add_argument("--neb-freeze-indices", nargs="+", type=int)
    parser.add_argument("--neb-freeze-elements", nargs="+")
    parser.add_argument("--neb-freeze-z-max", type=float)
    parser.add_argument("--neb-freeze-n-layers", type=int)

    args = parser.parse_args()
    
    # Handle --save-config
    if args.save_config:
        # Create template config
        template_config = NEBConfig(
            model_path=Path("/path/to/model.pt"),
            n_images=8,
            max_iterations=3000,
            device="cuda"
        )
        template_config.to_json(args.save_config)
        print(f"Configuration template saved to: {args.save_config}")
        print("\nEdit the file and use with: eon-neb initial.con final.con --config template.json")
        return 0
    
    # Validate inputs
    # Load or create config
    if args.config:
        print(f"Loading configuration from: {args.config}")
        config = NEBConfig.from_json(args.config)
    else:
        if not args.model:
            parser.error("--model is required when not using --config")
        
        config = NEBConfig(
            model_path=args.model,
            n_images=args.images,
            max_iterations=args.max_iter,
            device=args.device,
            freeze_strategy=args.freeze_strategy,
            freeze_indices=args.freeze_indices,
            freeze_elements=args.freeze_elements,
            freeze_z_max=args.freeze_z_max,
            freeze_n_layers=args.freeze_n_layers,
            
            min_freeze_strategy=args.min_freeze_strategy,
            min_freeze_indices=args.min_freeze_indices,
            min_freeze_elements=args.min_freeze_elements,
            min_freeze_z_max=args.min_freeze_z_max,
            min_freeze_n_layers=args.min_freeze_n_layers,
            
            neb_freeze_strategy=args.neb_freeze_strategy,
            neb_freeze_indices=args.neb_freeze_indices,
            neb_freeze_elements=args.neb_freeze_elements,
            neb_freeze_z_max=args.neb_freeze_z_max,
            neb_freeze_n_layers=args.neb_freeze_n_layers,
        )

    # Set working directory
    workdir = args.workdir if args.workdir else Path.cwd()

    # ================================
    # Execution mode selection
    # ================================

    # JSON batch mode
    if args.json:
        print("\n" + "="*60)
        print("eOn NEB RUNNER (JSON batch mode)")
        print("="*60)
        
        runner = NEBRunner(config)
        runner.run_from_json(args.json, workdir)
        return 0

    # Single NEB mode → require inputs
    if not args.initial or not args.final:
        parser.error("initial and final structure files are required (unless using --json)")
        
    # Run NEB
    print("\n" + "="*60)
    print("eOn NEB RUNNER")
    print("="*60)
    print(f"Model: {config.model_path}")
    print(f"Device: {config.device}")
    print(f"Images: {config.n_images}")
    print(f"Max iterations: {config.max_iterations}")
    print()
    
    runner = NEBRunner(config)
    result = runner.run_from_files(args.initial, args.final, workdir)
    
    # Print summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    if result.success:
        print("✓ NEB calculation completed successfully\n")
        print(f"Reaction energy: {result.reaction_energy:8.3f} eV")
        print(f"Forward barrier: {result.forward_barrier:8.3f} eV")
        print(f"Reverse barrier: {result.reverse_barrier:8.3f} eV")
        print(f"\nResults saved to: {result.neb_path}/summary.json")
        return 0
    else:
        print("✗ NEB calculation failed\n")
        print(f"Error: {result.error_message}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
