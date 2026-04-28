"""Configuration management for NEB calculations."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Set, Dict, Any, List
import json


@dataclass
class NEBConfig:
    """Configuration for NEB calculations.
    
    Attributes:
        model_path: Path to the ML potential checkpoint
        n_images: Number of intermediate NEB images
        max_iterations: Maximum NEB iterations
        device: Computing device ('cuda' or 'cpu')
        metals: Set of metal element symbols to freeze
        endpoint_min_settings: Settings for endpoint minimization
        neb_settings: Additional NEB-specific settings
    """
    
    model_path: Path
    n_images: int = 8
    max_iterations: int = 3000
    device: str = "cuda"

    # Global defaults
    freeze_strategy: str = "none"
    freeze_indices: Optional[List[int]] = None
    freeze_elements: Optional[List[str]] = None
    freeze_z_max: Optional[float] = None
    freeze_n_layers: Optional[int] = None
    
    # Stage-specific overrides
    min_freeze_strategy: Optional[str] = None
    min_freeze_indices: Optional[List[int]] = None
    min_freeze_elements: Optional[List[str]] = None
    min_freeze_z_max: Optional[float] = None
    min_freeze_n_layers: Optional[int] = None
    
    neb_freeze_strategy: Optional[str] = None
    neb_freeze_indices: Optional[List[int]] = None
    neb_freeze_elements: Optional[List[str]] = None
    neb_freeze_z_max: Optional[float] = None
    neb_freeze_n_layers: Optional[int] = None

    # Metals to freeze in slab calculations
    metals: Set[str] = field(default_factory=lambda: {
        "Pt", "Ni", "Fe", "Co", "Cu", "Ag", "Au", "Pd",
        "Ir", "Rh", "Ru", "Os", "Re", "W", "Mo", "Cr",
        "V", "Ti", "Mn", "Zn", "Al", "Ce"  # Added Ce for CeFe oxide
    })
    
    # Endpoint minimization settings
    endpoint_min_settings: Dict[str, Any] = field(default_factory=lambda: {
        "opt_method": "FIRE",
        "max_iterations": 75,
        "max_move": 0.07,
        "converged_force": 0.05,
    })
    
    # NEB-specific settings
    neb_settings: Dict[str, Any] = field(default_factory=lambda: {
        "spring": 4.0,
        "climbing_image_method": True,
        "ci_after": 0.2,
        "energy_weighted": True,
        "ew_ksp_min": 0.99,
        "ew_ksp_max": 2.59,
    })
    
    def __post_init__(self):
        """Convert model_path to Path object if it's a string."""
        if isinstance(self.model_path, str):
            self.model_path = Path(self.model_path)
    
    @classmethod
    def from_json(cls, json_path: Path) -> "NEBConfig":
        """Load configuration from JSON file.
        
        Args:
            json_path: Path to JSON configuration file
            
        Returns:
            NEBConfig instance
        """
        with open(json_path) as f:
            data = json.load(f)
        
        # Convert nested dicts if present
        if "metals" in data and isinstance(data["metals"], list):
            data["metals"] = set(data["metals"])
            
        return cls(**data)
    
    def to_json(self, json_path: Path):
        """Save configuration to JSON file.
        
        Args:
            json_path: Path to output JSON file
        """
        data = {
            "model_path": str(self.model_path),
            "n_images": self.n_images,
            "max_iterations": self.max_iterations,
            "device": self.device,
            "metals": list(self.metals),
            "endpoint_min_settings": self.endpoint_min_settings,
            "neb_settings": self.neb_settings,
        }
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_eon_config(self, job_type: str = "neb") -> Dict[str, Any]:
        """Generate eOn configuration dictionary.
        
        Args:
            job_type: Type of eOn job ('minimization' or 'neb')
            
        Returns:
            Configuration dictionary for eOn
        """
        base_config = {
            "Main": {
                "random_seed": 42567,
                "write_log": True,
            },
            "Potential": {
                "potential": "Metatomic",
            },
            "Metatomic": {
                "model_path": str(self.model_path.resolve()),
                "device": self.device,
            },
        }
        
        if job_type == "minimization":
            base_config["Main"]["job"] = "minimization"
            base_config["Optimizer"] = self.endpoint_min_settings
            base_config["FIRE"] = {
                "time_step": 0.1,
                "time_step_max": 0.5,
            }
            base_config["Debug"] = {
                "write_movies": True,
                "write_movies_interval": 5,
            }
            
        elif job_type == "neb":
            base_config["Main"]["job"] = "nudged_elastic_band"
            
            base_config["Nudged Elastic Band"] = {
                "images": self.n_images,
                "initializer": "idpp",
                "minimize_endpoints": "false",
                "neb_max_iterations": self.max_iterations,
                "converged_force": 0.05,
                **{k: str(v).lower() if isinstance(v, bool) else v 
                   for k, v in self.neb_settings.items()}
            }
            
            base_config["Optimizer"] = {
                "opt_method": "fire",
                "max_iterations": self.max_iterations,
                "max_move": 0.1,
                "converged_force": 0.05,
            }
            
            base_config["FIRE"] = {
                "time_step": 0.1,
                "time_step_max": 1.0,
            }
            
            base_config["Debug"] = {
                "write_movies": "false",
                "write_movies_interval": 50,
            }
        
        return base_config
        
    def with_overrides(self, **kwargs):
        return NEBConfig(
            **{**self.__dict__, **kwargs}
        )