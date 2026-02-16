"""PyTorch Lightning Trainer factory with sensible defaults."""

from typing import Optional, Iterable
from omegaconf import DictConfig, OmegaConf
import pytorch_lightning as pl


def create_trainer_with_defaults(
    trainer_cfg: DictConfig,
    logger: Optional[pl.loggers.Logger] = None,
    callbacks: Optional[Iterable[pl.Callback]] = None,
) -> pl.Trainer:
    """Create Lightning Trainer from Hydra config.
    
    Args:
        trainer_cfg: Hydra config for trainer parameters
        logger: Optional logger instance
        callbacks: Optional list of callbacks
    
    Returns:
        Configured PyTorch Lightning Trainer
    
    Example:
        from mura.hydra import create_trainer_with_defaults, EnhancedGitCallback
        
        trainer = create_trainer_with_defaults(
            cfg.trainer,
            logger=wandb_logger,
            callbacks=[checkpoint_cb, lr_cb, EnhancedGitCallback()]
        )
    """
    trainer_kwargs = OmegaConf.to_container(trainer_cfg, resolve=True)
    
    if logger is not None:
        trainer_kwargs["logger"] = logger
    if callbacks is not None:
        trainer_kwargs["callbacks"] = list(callbacks)
    
    return pl.Trainer(**trainer_kwargs)
