import os
import logging
from dataclasses import dataclass, field, asdict
import toml

from lightning.pytorch import seed_everything
from .callbacks import GitTrackerCallback
from .version import VersionManager
# from .train_support import *
# from .schema import validate


class data_run():
    def __init__(self, config):
    # validate(config)  # Validate config schema    # TODO
        self.config = config

    def __enter__(self):
        # Initialize version manager, create run directory, and set up logging
        self.version_manager = VersionManager(self.config.logging.base_path)
        self.version_data = self.version_manager.load_version()
        self.config.logging.run_path, self.config.logging.run_id, self.config.logging.version = \
            self.version_manager.new_path(self.config.logging.task_name, self.config.logging.run_name)
        self.run_path = self.config.logging.run_path
        # Initialize environment
        seed_everything(self.config.seed)
    
        # Save config to run directory
        self.config_dict = asdict(self.config)
        # print(self.config_dict, self.config)
        self.config_path = os.path.join(self.run_path,"config.toml")
        with open(self.config_path, 'w') as f:
            toml.dump(self.config_dict, f)
            
        return self.run_path

    def __exit__(self, exc_type, exc_value, traceback):

        # Finalize version info
        self.version_manager.finalize_run_info(self.run_path, self.config)
        
        # don't suppress exceptions
        if exc_type is not None:
            print(f"Exception occurred: {exc_value} of type {exc_type} \n Traceback: {traceback}")
            return False
        return True

