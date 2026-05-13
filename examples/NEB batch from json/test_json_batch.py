#!/usr/bin/env python
"""
Test script to verify the NEB batch JSON parsing and structure loading.

This script validates that:
1. The JSON file can be parsed correctly
2. Structures are properly loaded from pymatgen format
3. The runner can deserialize structures without errors
"""

from pathlib import Path
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from eon_neb.runner import NEBRunner
from eon_neb.config import NEBConfig
from pymatgen.io.json import MontyDecoder


def test_json_parsing():
    """Test that the JSON file can be parsed."""
    json_file = Path(__file__).parent / "neb_batch.json"
    
    print(f"\n{'='*60}")
    print("TEST 1: JSON File Parsing")
    print(f"{'='*60}")
    
    if not json_file.exists():
        print(f"❌ ERROR: {json_file} not found!")
        return False
    
    try:
        with open(json_file) as f:
            # Try with MontyDecoder first
            try:
                jobs = json.load(f, cls=MontyDecoder)
                print(f"✓ Successfully parsed with MontyDecoder")
            except TypeError:
                # Fall back to regular JSON
                f.seek(0)
                jobs = json.load(f)
                print(f"✓ Successfully parsed with regular JSON decoder")
        
        print(f"✓ Found {len(jobs)} NEB job(s)")
        return True, jobs
        
    except Exception as e:
        print(f"❌ ERROR parsing JSON: {e}")
        return False, None


def test_structure_loading(jobs):
    """Test that structures can be loaded from JSON dicts."""
    print(f"\n{'='*60}")
    print("TEST 2: Structure Loading from JSON")
    print(f"{'='*60}")
    
    # Create a dummy config for testing
    try:
        config = NEBConfig(model_path=Path("/dummy/model.pt"))
    except FileNotFoundError:
        # This is expected since we don't have a real model
        # Create config without checking model existence
        config = NEBConfig.__new__(NEBConfig)
        config.model_path = Path("/dummy/model.pt")
        config.freeze_strategy = "none"
    
    runner = NEBRunner.__new__(NEBRunner)
    runner.config = config
    
    for i, job in enumerate(jobs):
        comment = job.get("comment", f"job_{i}")
        print(f"\n  Job {i+1}: {comment}")
        
        try:
            # Test initial structure
            initial = runner.atoms_from_dict(job["initial"])
            print(f"    ✓ Initial structure loaded: {len(initial)} atoms")
            
            # Test final structure
            final = runner.atoms_from_dict(job["final"])
            print(f"    ✓ Final structure loaded: {len(final)} atoms")
            
            # Verify atom counts match
            if len(initial) != len(final):
                print(f"    ⚠ WARNING: Atom count mismatch ({len(initial)} vs {len(final)})")
            else:
                print(f"    ✓ Atom counts match")
            
        except Exception as e:
            print(f"    ❌ ERROR loading structures: {e}")
            return False
    
    return True


def test_structure_details(jobs):
    """Print details about the structures."""
    print(f"\n{'='*60}")
    print("TEST 3: Structure Details")
    print(f"{'='*60}")
    
    for i, job in enumerate(jobs[:1]):  # Just show first job
        comment = job.get("comment", f"job_{i}")
        print(f"\nJob: {comment}")
        
        initial = job["initial"]
        final = job["final"]
        
        print(f"\nInitial structure:")
        if "lattice" in initial:
            lattice = initial["lattice"]
            print(f"  Lattice type: {initial.get('@class', 'unknown')}")
            print(f"  Cell parameters: a={lattice.get('a', 0):.3f}, "
                  f"b={lattice.get('b', 0):.3f}, c={lattice.get('c', 0):.3f}")
            print(f"  PBC: {lattice.get('pbc', [True, True, True])}")
            print(f"  Number of sites: {len(initial.get('sites', []))}")
        
        print(f"\nFinal structure:")
        if "lattice" in final:
            lattice = final["lattice"]
            print(f"  Lattice type: {final.get('@class', 'unknown')}")
            print(f"  Cell parameters: a={lattice.get('a', 0):.3f}, "
                  f"b={lattice.get('b', 0):.3f}, c={lattice.get('c', 0):.3f}")
            print(f"  PBC: {lattice.get('pbc', [True, True, True])}")
            print(f"  Number of sites: {len(final.get('sites', []))}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("NEB BATCH JSON VALIDATION TEST")
    print("="*60)
    
    # Test 1: JSON parsing
    result = test_json_parsing()
    if not result[0]:
        print("\n❌ FAILED: JSON parsing test")
        return 1
    
    jobs = result[1]
    
    # Test 2: Structure loading
    if not test_structure_loading(jobs):
        print("\n❌ FAILED: Structure loading test")
        return 1
    
    # Test 3: Structure details
    if not test_structure_details(jobs):
        print("\n❌ FAILED: Structure details test")
        return 1
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nThe JSON file is properly formatted and ready for NEB calculations.")
    print("\nTo run the actual NEB batch calculation:")
    print(f"  eon-neb --json neb_batch.json --model <path/to/model.pt>")
    print("\nOr from Python:")
    print(f"  from eon_neb.runner import NEBRunner")
    print(f"  runner = NEBRunner(config)")
    print(f"  results = runner.run_from_json('neb_batch.json', workdir)")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
