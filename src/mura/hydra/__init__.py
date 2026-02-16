"""Hydra-compatible utilities from Mura.

This module provides Hydra-friendly versions of Mura's functionality:
- OmegaConf resolvers for git info, timestamps, etc.
- Lightning callbacks for version tracking, git tracking
- Factory functions for common patterns
"""

from .resolvers import register_resolvers, compute_git_info, generate_sec_id
from .callbacks import EnhancedGitCallback, VersionTrackerCallback
from .logger import create_wandb_logger
from .trainer import create_trainer_with_defaults
from .cache import CacheManager, compute_config_hash

__all__ = [
    "register_resolvers",
    "compute_git_info",
    "generate_sec_id",
    "EnhancedGitCallback",
    "VersionTrackerCallback",
    "create_wandb_logger",
    "create_trainer_with_defaults",
    "CacheManager",
    "compute_config_hash",
]
