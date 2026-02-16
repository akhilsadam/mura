"""Dataset caching utilities.

Provides hash-based caching for generated datasets with automatic versioning.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar
import torch

T = TypeVar('T')


def compute_config_hash(config_dict: Dict[str, Any], keys: Optional[list] = None) -> str:
    """Compute deterministic hash from config parameters.
    
    Args:
        config_dict: Configuration dictionary
        keys: Optional list of keys to include in hash (uses all if None)
    
    Returns:
        12-character hex hash string
    """
    if keys:
        filtered = {k: config_dict.get(k) for k in keys if k in config_dict}
    else:
        filtered = config_dict
    
    cfg_str = json.dumps(filtered, sort_keys=True)
    return hashlib.sha256(cfg_str.encode()).hexdigest()[:12]


class CacheManager:
    """Manages cached datasets with version tracking.
    
    Example:
        cache = CacheManager(cache_root="data/cache", version="v1")
        
        data = cache.load_or_generate(
            config={'grid_size': 128, 'samples': 1000},
            generator_fn=generate_data,
            cache_keys=['grid_size', 'samples']  # Only hash these params
        )
    """
    
    def __init__(self, cache_root: str, version: str = "v1"):
        """
        Args:
            cache_root: Root directory for cache
            version: Version string (allows format evolution)
        """
        self.cache_root = Path(cache_root)
        self.version = version
        self.cache_root.mkdir(parents=True, exist_ok=True)
    
    def get_cache_path(self, config_hash: str, name: str = "data") -> Path:
        """Get cache directory for a config hash."""
        cache_dir = self.cache_root / f"{name}_{self.version}_{config_hash}"
        return cache_dir
    
    def load_or_generate(
        self,
        config: Dict[str, Any],
        generator_fn: Callable[[Dict[str, Any], Path], T],
        cache_keys: Optional[list] = None,
        force_regenerate: bool = False,
        name: str = "data",
    ) -> T:
        """Load cached data or generate if not found.
        
        Args:
            config: Configuration dictionary
            generator_fn: Function that generates data, receives (config, cache_path)
            cache_keys: Optional list of config keys to use for hashing
            force_regenerate: If True, ignore cache and regenerate
            name: Name prefix for cache directory
        
        Returns:
            Loaded or generated data
        """
        config_hash = compute_config_hash(config, cache_keys)
        cache_dir = self.get_cache_path(config_hash, name)
        cache_file = cache_dir / "data.pt"
        
        if cache_file.exists() and not force_regenerate:
            print(f"Loading cached data from {cache_dir}")
            checkpoint = torch.load(cache_file, weights_only=False)
            return checkpoint['data']
        else:
            print(f"Generating data (will cache to {cache_dir})")
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate data
            data = generator_fn(config, cache_dir)
            
            # Save to cache
            torch.save({
                'data': data,
                'config': config,
                'version': self.version,
            }, cache_file)
            
            # Save metadata
            metadata_file = cache_dir / "metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({
                    'config': config,
                    'version': self.version,
                    'config_hash': config_hash,
                }, f, indent=2)
            
            return data
