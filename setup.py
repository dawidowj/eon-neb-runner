#!/usr/bin/env python
"""Setup script for eOn NEB runner."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="eon-neb-runner",
    version="0.1.0",
    description="NEB calculations with eOn and ML potentials",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",  # Update this
    author_email="your.email@example.com",  # Update this
    url="https://github.com/yourusername/eon-neb-runner",  # Update when you have a repo
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.20",
        "ase>=3.22",
        "rgpycrumbs>=1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
        "gpu": [
            "torch>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eon-neb=eon_neb.cli:main",
            "eon-neb-test=tests.test_installation:run_tests",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="neb nudged-elastic-band machine-learning chemistry materials",
)
