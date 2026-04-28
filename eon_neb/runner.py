"""Main NEB runner implementation."""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple
import subprocess
import json
import numpy as np
from ase.io import read, write
from ase.constraints import FixAtoms
from ase import Atoms

try:
    from rgpycrumbs.eon.helpers import write_eon_config
except ImportError:
    raise ImportError(
        "rgpycrumbs not found. Install with: pip install rgpycrumbs"
    )

from .config import NEBConfig


@dataclass
class NEBResult:
    """Results from a NEB calculation.
    
    Attributes:
        success: Whether the calculation completed successfully
        reaction_energy: Energy difference between products and reactants (eV)
        forward_barrier: Forward activation barrier (eV)
        reverse_barrier: Reverse activation barrier (eV)
        ts_index: Index of the transition state image
        ts_energy: Energy of the transition state (eV)
        neb_path: Path to directory containing NEB results
        error_message: Error message if calculation failed
    """
    success: bool
    reaction_energy: Optional[float] = None
    forward_barrier: Optional[float] = None
    reverse_barrier: Optional[float] = None
    ts_index: Optional[int] = None
    ts_energy: Optional[float] = None
    neb_path: Optional[Path] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "reaction_energy_eV": self.reaction_energy,
            "forward_barrier_eV": self.forward_barrier,
            "reverse_barrier_eV": self.reverse_barrier,
            "ts_index": self.ts_index,
            "ts_energy_eV": self.ts_energy,
            "neb_path": str(self.neb_path) if self.neb_path else None,
            "error_message": self.error_message,
        }
    
    def to_json(self, json_path: Path):
        """Save result to JSON file."""
        with open(json_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


class NEBRunner:
    """Runner for NEB calculations with ML potentials.
    
    This class handles the complete NEB workflow:
    1. Endpoint minimization
    2. Structure preprocessing
    3. NEB calculation
    4. Result extraction
    """
    
    def __init__(self, config: NEBConfig):
        """Initialize NEB runner.
        
        Args:
            config: NEB configuration
        """
        self.config = config
        
        # Verify model exists
        if not self.config.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.config.model_path}"
            )


    def atoms_from_dict(self, d: dict) -> Atoms:
        """Convert JSON dict to ASE Atoms."""
        return Atoms(
            symbols=d["symbols"],
            positions=d["positions"],
            cell=d["cell"],
            pbc=d["pbc"]
        )
    

    def get_constraints(self, atoms: Atoms, stage: str = "neb") -> FixAtoms:
        """Build constraints based on config and stage."""
        
        n = len(atoms)
        mask = np.zeros(n, dtype=bool)
    
        # =========================
        # Resolve stage-specific settings
        # =========================
        if stage == "min":
            strategy = self.config.min_freeze_strategy or self.config.freeze_strategy
            indices = self.config.min_freeze_indices or self.config.freeze_indices
            elements = self.config.min_freeze_elements or self.config.freeze_elements
            zmax = self.config.min_freeze_z_max or self.config.freeze_z_max
            n_layers = self.config.min_freeze_n_layers or self.config.freeze_n_layers
    
        elif stage == "neb":
            strategy = self.config.neb_freeze_strategy or self.config.freeze_strategy
            indices = self.config.neb_freeze_indices or self.config.freeze_indices
            elements = self.config.neb_freeze_elements or self.config.freeze_elements
            zmax = self.config.neb_freeze_z_max or self.config.freeze_z_max
            n_layers = self.config.neb_freeze_n_layers or self.config.freeze_n_layers
    
        else:
            raise ValueError(f"Unknown stage: {stage}")
    
        # =========================
        # Apply strategy
        # =========================
        if strategy == "none":
            return FixAtoms(mask=mask)
    
        elif strategy == "index":
            for i in indices or []:
                if i < n:
                    mask[i] = True
    
        elif strategy == "element":
            elems = set(elements) if elements is not None else set(self.config.metals)
            for i, atom in enumerate(atoms):
                if atom.symbol in elems:
                    mask[i] = True
    
        elif strategy == "z":
            if zmax is None:
                raise ValueError("freeze_z_max must be set for z strategy")
            mask = atoms.positions[:, 2] < zmax
    
        elif strategy == "layers":
            from ase.geometry import get_layers
            tags, _ = get_layers(atoms, (0, 0, 1))
            min_tag = min(tags)
            for i, tag in enumerate(tags):
                if tag < min_tag + (n_layers or 1):
                    mask[i] = True
    
        else:
            raise ValueError(f"Unknown freeze_strategy: {strategy}")
    
        return FixAtoms(mask=mask)
        

    
    def preprocess_structure(self, atoms: Atoms, stage: str = "neb") -> Atoms:
        """Preprocess structure (wrap, apply constraints)."""
        atoms.wrap()
        atoms.set_constraint(self.get_constraints(atoms, stage=stage))
        return atoms
    
    def run_minimization(
        self, 
        atoms: Atoms, 
        workdir: Path,
        structure_name: str = "structure"
    ) -> Atoms:
        """Run eOn minimization.
        
        Args:
            atoms: Structure to minimize
            workdir: Working directory for minimization
            structure_name: Name for logging
            
        Returns:
            Minimized structure
            
        Raises:
            RuntimeError: If minimization fails
        """
        print(f"\n=== Minimizing {structure_name} in {workdir} ===")
        workdir.mkdir(parents=True, exist_ok=True)
        
        # Write structure
        write(workdir / "pos.con", atoms)
        
        # Get eOn config
        min_config = self.config.get_eon_config(job_type="minimization")
        write_eon_config(workdir / "config.ini", min_config)
        
        # Run eOn
        result = subprocess.run(
            ["eonclient"],
            cwd=workdir,
            capture_output=True,
            text=True
        )
        
        # Save logs
        (workdir / "stdout.txt").write_text(result.stdout)
        (workdir / "stderr.txt").write_text(result.stderr)
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Minimization failed for {structure_name}\n"
                f"See {workdir}/stderr.txt for details"
            )
        
        # Load minimized structure
        min_file = workdir / "min.con"
        if not min_file.exists():
            raise RuntimeError(f"Output file not found: {min_file}")
        
        minimized = read(min_file)
        print(f"✓ {structure_name} minimized successfully")
        
        return minimized
    
    def run_neb(
        self,
        initial: Atoms,
        final: Atoms,
        workdir: Path
    ) -> NEBResult:
        """Run complete NEB calculation.
        
        Args:
            initial: Initial structure (reactant)
            final: Final structure (product)
            workdir: Working directory for calculation
            
        Returns:
            NEBResult object with calculation results
        """
        try:
            workdir.mkdir(parents=True, exist_ok=True)
            
            # Sanity checks
            if len(initial) != len(final):
                raise ValueError("Atom count mismatch between initial and final")
            
            if list(initial.numbers) != list(final.numbers):
                raise ValueError("Atom ordering mismatch between initial and final")
            
            # Stage 1: Minimize endpoints
            print("\n" + "="*60)
            print("STAGE 1: ENDPOINT MINIMIZATION")
            print("="*60)
            
            initial = self.preprocess_structure(initial, stage="min")
            final = self.preprocess_structure(final, stage="min")
            
            initial_min = self.run_minimization(
                initial, 
                workdir / "reactant_min",
                "reactant"
            )
            
            final_min = self.run_minimization(
                final,
                workdir / "product_min", 
                "product"
            )
            
            # Stage 2: Preprocess 
            print("\n" + "="*60)
            print("STAGE 2: PREPROCESSING")
            print("="*60)
            
            initial_min = self.preprocess_structure(initial_min, stage="neb")
            final_min = self.preprocess_structure(final_min, stage="neb")
            
            # Enforce identical cell
            final_min.set_cell(initial_min.get_cell(), scale_atoms=True)
            
            constraint = initial_min.constraints[0]
            n_frozen = len(constraint.get_indices())
            print(f"Frozen atoms: {n_frozen}")
            
            # Write NEB inputs
            write(workdir / "reactant.con", initial_min)
            write(workdir / "product.con", final_min)
            
            # Stage 3: NEB
            print("\n" + "="*60)
            print("STAGE 3: NEB CALCULATION")
            print("="*60)
            
            neb_config = self.config.get_eon_config(job_type="neb")
            write_eon_config(workdir / "config.ini", neb_config)
            
            print("Starting eOn NEB...")
            result = subprocess.run(
                ["eonclient"],
                cwd=workdir,
                capture_output=True,
                text=True
            )
            
            # Save logs
            (workdir / "stdout.txt").write_text(result.stdout)
            (workdir / "stderr.txt").write_text(result.stderr)
            
            if result.returncode != 0:
                return NEBResult(
                    success=False,
                    error_message=f"eOn run failed. See {workdir}/stderr.txt",
                    neb_path=workdir
                )
            
            print("✓ eOn NEB completed successfully")
            
            # Parse results
            return self._parse_results(workdir)
            
        except Exception as e:
            return NEBResult(
                success=False,
                error_message=str(e),
                neb_path=workdir
            )
    
    def _parse_results(self, workdir: Path) -> NEBResult:
        """Parse NEB results from output files.
        
        Args:
            workdir: Directory containing NEB results
            
        Returns:
            NEBResult object
        """
        print("\n" + "="*60)
        print("NEB RESULTS")
        print("="*60)
        
        neb_dat = workdir / "neb.dat"
        if not neb_dat.exists():
            return NEBResult(
                success=False,
                error_message=f"neb.dat not found in {workdir}",
                neb_path=workdir
            )
        
        try:
            data = np.loadtxt(neb_dat, skiprows=1)
            
            energy = data[:, 2]
            E_reactant = energy[0]
            E_product = energy[-1]
            
            # Find transition state
            ts_idx = int(np.argmax(energy))
            E_ts = energy[ts_idx]
            
            # Calculate barriers
            E_fwd = E_ts - E_reactant
            E_rev = E_ts - E_product
            dE_rxn = E_product - E_reactant
            
            print(f"Reaction energy (ΔE): {dE_rxn:8.3f} eV")
            print(f"Forward barrier:      {E_fwd:8.3f} eV")
            print(f"Reverse barrier:      {E_rev:8.3f} eV")
            print(f"TS image index:       {ts_idx}")
            
            result = NEBResult(
                success=True,
                reaction_energy=float(dE_rxn),
                forward_barrier=float(E_fwd),
                reverse_barrier=float(E_rev),
                ts_index=ts_idx,
                ts_energy=float(E_ts),
                neb_path=workdir
            )
            
            # Save JSON summary
            result.to_json(workdir / "summary.json")
            
            return result
            
        except Exception as e:
            return NEBResult(
                success=False,
                error_message=f"Failed to parse neb.dat: {str(e)}",
                neb_path=workdir
            )
    
    def run_from_files(
        self,
        initial_file: Path,
        final_file: Path,
        workdir: Optional[Path] = None
    ) -> NEBResult:
        """Run NEB from structure files.
        
        Args:
            initial_file: Path to initial structure file
            final_file: Path to final structure file
            workdir: Working directory (default: current directory)
            
        Returns:
            NEBResult object
        """
        if workdir is None:
            workdir = Path.cwd()
        
        print(f"Loading structures...")
        print(f"  Initial: {initial_file}")
        print(f"  Final:   {final_file}")
        
        initial = read(initial_file)
        final = read(final_file)
        
        return self.run_neb(initial, final, workdir)
        
    def run_from_json(self, json_file: Path, base_workdir: Path) -> dict:
        """Run NEBs from JSON input with embedded structures."""
        
        with open(json_file) as f:
            jobs = json.load(f)
        
            results = {}
    
        for i, job in enumerate(jobs):
            name = job.get("comment", f"job_{i}")
            
            print("\n" + "#"*70)
            print(f"RUNNING: {name}")
            print("#"*70)
        
            # Convert dict → ASE
            initial = self.atoms_from_dict(job["initial"])
            final = self.atoms_from_dict(job["final"])
            
            # ================================
            # NEW: config overrides per job
            # ================================
            job_config = self.config.with_overrides(
                freeze_strategy=job.get("freeze_strategy"),
                freeze_indices=job.get("freeze_indices"),
                freeze_z_max=job.get("freeze_z_max"),
                freeze_n_layers=job.get("freeze_n_layers"),
            )
            
            workdir = base_workdir / name.replace(" ", "_")
            workdir.mkdir(parents=True, exist_ok=True)
            
            result = self.run_neb(initial, final, workdir)
            results[name] = result.to_dict()

        # Save batch summary
        with open(base_workdir / "batch_summary.json", "w") as f:
            json.dump(results, f, indent=2)
    
        return results