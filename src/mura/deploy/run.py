import os, importlib, logging
import torch
from lightning.pytorch.loggers import WandbLogger

from mura.repo.git_utils import understand_env
from mura.deploy.util import cprint
from mura.deploy.set_gpu import set_gpu

def run(args):
    
    version, action_id, task_id, run_id, paramfile, logfile = args[1:]
    
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    py_logger = logging.getLogger('auto')
    py_logger.setLevel(logging.INFO)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    py_logger.addHandler(consoleHandler)

    fileHandler = logging.FileHandler(logfile)
    fileHandler.setFormatter(logFormatter)
    py_logger.addHandler(fileHandler)
        
    # load class 'param' from inside from paramfile.
    module_name = 'param'
    module_path = os.path.join(os.getcwd(), paramfile)
    
    if os.path.exists(module_path):
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Now you can use the module
    else:
        py_logger.warn(f"File not found: {module_path}")
    _config = module
    
    if hasattr(_config, 'config'):
        config = _config.config
        param = config.actions[action_id].tasks[task_id].run[run_id]
        action = config.actions[action_id]
        task = action.tasks[task_id]
        action_name = action.action_name
        task_name = task.task_name
        run_name = param.name if hasattr(param, 'name') else ''
        ngpu = action.ngpu
        project_name = config.project_name
    else:
        print(_config)
        param = _config.param
        action_name = ''
        task_name = ''
        run_name = param.name if hasattr(param, 'name') else ''
        ngpu = 1
        project_name = param.project_name
        
    param.gpus = set_gpu(ngpu)
    
    version, task, save_path = understand_env()
    fname = version + '.' + '.'.join([action_id, task_id, run_id])
    if action_name:
        fname += '-' + action_name
    if task_name:
        fname += '-' + task_name
    if run_name:
        fname += '-' + run_name

    # os.makedirs(os.path.join(save_path,"wandb/"), exist_ok=True)
    wandb_logger = WandbLogger(project=project_name, name=fname,
                    version=fname, config=param)
                    # save_dir=save_path) # has issues with sync.
                    
                    
    # TODO add watch stuff from train.py
                    
    return param, wandb_logger, py_logger, version, save_path