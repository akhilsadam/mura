import os
# from schema import Schema, And, Use, Optional, Or

from mura.deploy.util import crupdate, cprint
from mura.deploy.deploy_action import deploy, deploy_action
from mura.repo.git_utils import git_utils as gl

# param_schema = Schema({
#     'grid': {
#         'Nx': int,
#         'Ny': int,
#         'Lx': float,
#         'Ly': float,
#     },
# })
                    
class run:
    env_init_template = 'sg_env_init.jinja'
    env_end_template = 'sg_env_end.jinja'
    submit_template = 'sg_engine.jinja'    ## jobname, logfile, run_commands
    run_template = 'run.jinja'          ## env_init_commands, env_end_commands, {{runner}} {{run}} {{configfile}} {{logfile}}
    param_file = 'param.py'
    
    install_info = 'install'

class action:
        action_name = 'action'
        no_compute = False
        strict_version_checks = False
        base_save_path = '../run/' # outside source folder
        #----
        
        debug = False
        save_frequency = 100 # only for ML
        ngpu = 1
        data = "" # only for ML; data folder

class DefaultScheduler():    
    def __init__(self, _params):
        self.__name__ = 'config'
        self.run = run
        self.actions = \
            [
                action,
            ]

        if _params is not None:
            crupdate(self,_params)

class Instancer():
    def __init__(self, run_validator, config=None, gconfig=None):
        self.__name__ = 'Instancer'
        self.defaults = DefaultScheduler(config)
        gdict = gconfig.__dict__ if gconfig is not None else {}
        self.gl = gl(**gdict, repo_path=os.getcwd())
        
        if run_validator is not None:
            self.validate(run_validator)
        
    def validate(self, run_validator):
        # go into each action, task, run, and validate
        for i,_action in enumerate(self.defaults.actions):
            for j,_task in enumerate(_action.tasks):
                for k,_run in enumerate(_task.runs):
                    print(_task, _run)
                    self.defaults.actions[i].tasks[j].runs[k] = run_validator(_run)
        
    def run(self):
        deploy(lambda *x: deploy_action(*x,self.gl), self.defaults, [], 'actions', self.defaults)

            
    def __repr__(self):
        return f'Scheduler: \n\t{cprint(self.defaults,level=1)}\nGit: \n\t{cprint(self.gl,level=1)}'
        
            
class SingleInstancer(Instancer):
    def __init__(self, run_validator, config, param=None, gconfig=None, _task_name='', _action_name='', **action_kwargs):
        class task:
            task_name = _task_name
            runs = [param,]
        class action:
            action_name = _action_name
            tasks = [task,]
    
        for key, value in action_kwargs.items():
            setattr(action, key, value)    
        
        config.actions = [action,]        
        super().__init__(run_validator=run_validator, config=config, gconfig=gconfig)