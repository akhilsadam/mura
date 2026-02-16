"""WandB logger factory with sensible defaults."""

from typing import Optional, Dict, Any
from omegaconf import DictConfig, OmegaConf
from lightning.pytorch.loggers import WandbLogger


def create_wandb_logger(
    wandb_cfg: DictConfig,
    git_info: Optional[Dict[str, Any]] = None,
    version_id: Optional[str] = None,
) -> WandbLogger:
    """Create WandB logger with enhanced configuration.
    
    Args:
        wandb_cfg: Hydra config for WandB (project, entity, etc.)
        git_info: Optional git information to log
        version_id: Optional version/run ID
    
    Returns:
        Configured WandB logger
    
    Example:
        from mura.hydra import create_wandb_logger, compute_git_info
        
        git_info = compute_git_info()
        logger = create_wandb_logger(
            cfg.wandb,
            git_info=git_info,
            version_id=cfg.get('run_id')
        )
    """
    # Convert to container, filtering out None/empty values
    wandb_kwargs = OmegaConf.to_container(wandb_cfg, resolve=True)
    wandb_kwargs = {k: v for k, v in wandb_kwargs.items() if v not in (None, "")}
    
    # Create logger
    logger = WandbLogger(**wandb_kwargs, log_model=False)
    
    # Log additional info
    if git_info:
        logger.experiment.config.update({
            "git_sha": git_info.get('sha'),
            "git_dirty": git_info.get('dirty'),
        })
    
    if version_id:
        logger.experiment.config.update({
            "version_id": version_id,
        })
    
    return logger
