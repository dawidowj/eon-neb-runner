"""Installation and environment tests for eOn NEB runner."""

import unittest
import subprocess
import sys
from pathlib import Path
import importlib


class TestInstallation(unittest.TestCase):
    """Test that all dependencies are correctly installed."""
    
    def test_python_version(self):
        """Test Python version is 3.10+."""
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3)
        self.assertGreaterEqual(version.minor, 10)
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    def test_ase_import(self):
        """Test ASE is installed."""
        try:
            import ase
            print(f"✓ ASE {ase.__version__}")
        except ImportError:
            self.fail("ASE not installed. Install with: pip install ase")
    
    def test_numpy_import(self):
        """Test NumPy is installed."""
        try:
            import numpy as np
            print(f"✓ NumPy {np.__version__}")
        except ImportError:
            self.fail("NumPy not installed. Install with: pip install numpy")
    
    def test_rgpycrumbs_import(self):
        """Test rgpycrumbs is installed."""
        try:
            import rgpycrumbs
            from rgpycrumbs.eon.helpers import write_eon_config
            print(f"✓ rgpycrumbs available")
        except ImportError:
            self.fail("rgpycrumbs not installed. Install with: pip install rgpycrumbs")
    
    def test_eon_executable(self):
        """Test eOn (eonclient) is available."""
        try:
            result = subprocess.run(
                ["eonclient", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # eOn might not have --version, so just check it runs
            print(f"✓ eonclient executable found")
        except FileNotFoundError:
            self.fail(
                "eonclient not found in PATH. "
                "Make sure eOn is installed and activated in conda environment."
            )
        except subprocess.TimeoutExpired:
            # If it times out, it's still found
            print(f"✓ eonclient executable found")
    
    def test_cuda_available(self):
        """Test CUDA availability (warning only)."""
        try:
            import torch
            if torch.cuda.is_available():
                print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                print("⚠ CUDA not available - will run on CPU (slower)")
        except ImportError:
            print("⚠ PyTorch not found - cannot check CUDA")
    
    def test_package_import(self):
        """Test this package can be imported."""
        try:
            import eon_neb
            from eon_neb import NEBRunner, NEBConfig
            print(f"✓ eon_neb package {eon_neb.__version__}")
        except ImportError as e:
            self.fail(f"Cannot import eon_neb: {e}")


class TestModelAccess(unittest.TestCase):
    """Test model file accessibility."""
    
    def test_default_model_path(self):
        """Test if default model path is accessible (skip if not configured)."""
        default_model = Path("/nfs/hpc/share/dawidowj/bin/MLIP_checkpoints/pet-mad-s-v1.5.0.pt")
        
        if default_model.exists():
            print(f"✓ Default PET-MAD model found: {default_model}")
        else:
            print(
                f"⚠ Default model not found at {default_model}\n"
                "  This is expected if running on a different system.\n"
                "  Specify model path with --model flag."
            )


def run_tests():
    """Run all installation tests."""
    print("="*60)
    print("INSTALLATION TESTS")
    print("="*60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestInstallation))
    suite.addTests(loader.loadTestsFromTestCase(TestModelAccess))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*60)
    if result.wasSuccessful():
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nInstallation successful! You can now use:")
        print("  eon-neb --help")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
