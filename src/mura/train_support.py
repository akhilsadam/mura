from dataclasses import asdict, make_dataclass
import logging, os

import iox
from models import models


logger = logging.getLogger(__name__)
# ----------------------------
# Supporting Functions
# ----------------------------

# def to_dataclass(my_dict):
#     return make_dataclass(
#         "Parameter", ((k, type(v)) for k, v in my_dict.items())
#     )(**my_dict)

def instantiate_model(config):
    """Dynamically create model based on config"""
    # Implementation from previous version
    model_module = models.get(config.model.name)
    param = config.model
    model = model_module.Network(param)
    return model

def get_data_loaders(config):
    """Create data loaders based on config"""
    # Implementation from previous version
    # start by checking if config.data.dataset is a folder path
    if isinstance(config.data.dataset, str) and os.path.isdir(config.data.dataset):
        dataloaders, shapes, _ = iox.load_data(config.data.dataset, asdict(config.data))
    else:
        dataloaders, shapes, _ = iox.datasets[config.data.dataset](asdict(config.data), config.logging.run_path)
    logger.info(f"Dataloaders created with shapes: {shapes}.")
    
    return dataloaders

def save_results(config, results):
    """Save results to run directory"""
    logger.info(f"Saving output to {config.logging.run_path}")
    pass
