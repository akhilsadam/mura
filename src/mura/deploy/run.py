import os
from lightning.pytorch.loggers import WandbLogger

from repo.git_utils import understand_env

def run(config, ml=True):

    version, task, save_path = understand_env()
    fname = '-'.join(config.task_path.split('/')[1:]) + f"-{config.run.id}"

    # which gpus are used?
    cvs = os.environ['CUDA_VISIBLE_DEVICES']
    cvs = [int(c) for c in cvs.split(',')] # convert to list of ints
    
    config.update({'which_gpu': cvs})

    # os.makedirs(os.path.join(save_path,"wandb/"), exist_ok=True)
    wandb_logger = WandbLogger(project=config.project_name, name=fname,
                    version=fname, config=config)
                    # save_dir=save_path) # has issues with sync.
                    
                    
    # TODO add watch stuff from train.py
                    
    return wandb_logger, version, task, save_path