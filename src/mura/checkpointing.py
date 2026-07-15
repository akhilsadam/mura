"""Unified checkpoint saving/loading with metadata."""
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pytorch_lightning as pl
import torch
from omegaconf import DictConfig, OmegaConf


def save_checkpoint(
    model: pl.LightningModule,
    path: str,
    cfg: DictConfig,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Save model checkpoint with config and metadata.

    Args:
        model: Lightning module to save
        path: Path to save checkpoint
        cfg: Hydra config
        metadata: Additional metadata (git info, study params, etc.)
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "model_state_dict": model.state_dict(),
        "config": OmegaConf.to_container(cfg, resolve=True),
        "metadata": metadata or {},
    }

    torch.save(checkpoint, path)
    print(f"✓ Checkpoint saved to {path}")


def load_checkpoint(path: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """Load checkpoint, config, and metadata.

    Args:
        path: Path to checkpoint

    Returns:
        (model_state_dict, config_dict, metadata)
    """
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Checkpoint not found: {path}")

    checkpoint = torch.load(path, map_location="cpu")

    model_state = checkpoint.get("model_state_dict", {})
    config = checkpoint.get("config", {})
    metadata = checkpoint.get("metadata", {})

    print(f"✓ Checkpoint loaded from {path}")
    return model_state, config, metadata
