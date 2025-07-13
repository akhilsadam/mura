import os
import logging
from dataclasses import dataclass, field, asdict
from omegaconf import OmegaConf, DictConfig, MISSING

import torch
import torch.nn as nn

from mura import lightning_run

# Set precision globally
torch.set_float32_matmul_precision('high')
logger = logging.getLogger(__name__)

# Structured configuration using Python classes
@dataclass
class ModelConfig:
    name: str = "sanity_check_single"
    learning_rate: float = 1e-3
    crit = nn.MSELoss()
    vcrit = nn.MSELoss()


@dataclass
class DataConfig:
    dataset_path: str = "./data"
    batch_size: int = 16
    num_workers: int = 8
    train_memory_length: int = 1
    train_predict_length: int = 1
    test_memory_length: int = 1
    test_predict_length: int = 1
    test_image_size: int = 64
    train_image_size: int = 64
    # augmentations: bool = False

@dataclass
class TrainerConfig:
    max_steps: int = 10000
    save_freq: int = 1000
    devices: int = 1
    accelerator: str = "auto"
    strategy: str = ""  # or "ddp", "deepspeed", "fsdp"
    # precision: str = "16-mixed"

@dataclass
class LoggingConfig:
    project: str = "delay-neural-operator"
    task_name: str = MISSING  # Must be provided
    run_name: str = MISSING  # Must be provided
    run_id: str = MISSING  # Must be provided
    version: list = field(default_factory = lambda: [0, 0, 0])  # Major, Minor, Patch
    base_path: str = "./run"
    run_path: str = ''
    version_file: str = "version.yml"
    notes: str = ""

@dataclass
class RootConfig:
    seed: int = 42
    pytest: bool = False
    model = ModelConfig()
    data = DataConfig()
    trainer = TrainerConfig()
    logging = LoggingConfig()


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    # Create base configuration
    base_config = RootConfig()
    
    lightning_run(base_config)