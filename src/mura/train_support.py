import logging, os

import iox
from models import models

from .schema import asdict


logger = logging.getLogger(__name__)
# ----------------------------
# Supporting Functions
# ----------------------------

def instantiate_model(config):
    """Dynamically create model based on config"""
    # Implementation from previous version
    model_module = models.get(config.model.name)
    # param = config.model
    model = model_module.Network(config)
    return model

def get_data_loaders(config):
    """Create data loaders based on config"""
    # Implementation from previous version
    # start by checking if config.data.dataset is a folder path
    if isinstance(config.data.dataset, str) and os.path.isdir(config.data.dataset):
        raise ValueError(f"Dataset path {config.data.dataset} is a directory, not a dataset name.")
        # dataloaders, shapes, _ = iox.load_data(config.data.dataset, asdict(config.data))
    else:
        dataloaders, shapes, _ = iox.datasets[config.data.dataset](config.model, asdict(config.data), config.logging.run_path)
    logger.info(f"Dataloaders created with shapes: {shapes}.")
    
    return dataloaders

def save_results(config, results):
    """Save results to run directory"""
    logger.info(f"[SKIP] Saving output to {config.logging.run_path}")
    pass
