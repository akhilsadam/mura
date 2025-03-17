import logging, os, copy

from mura.deploy.util import cupdate, cselect, serialize_class, check_wifi
from mura.deploy.templates import sg_engine, Bash, sg_engine_filename

code_folder = '.src'
run_folder = 'run'
run_info_file = 'param.py'

service_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../services/service_tmux.py')

## logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger('auto-deploy-action')
rootLogger.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)   

tasklogger = rootLogger.getChild('task')


def deploy(deploy_function, action_info, index, key, parent):
    for i, task in enumerate(action_info.__dict__[key]):
        task_info = copy.deepcopy(task)
        cupdate(task_info, action_info, [key])
        deploy_function(task_info, [*index,i], parent)

def deploy_action(action_info, i, parent, _gl):

    repo = _gl.repo(strict=action_info.strict_version_checks)
    version_data, source_modified_flag = _gl.tag_and_version(repo, tag=action_info.strict_version_checks)
    version, action, save_path = _gl.get_save_path(version_data, action_info.strict_version_checks, action_info.action_name, action_info.base_save_path)
    _gl.save_env(version, action, save_path)

    fileHandler = logging.FileHandler(f"{save_path}/version.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    logger = rootLogger
        
    hostname = os.uname()[1]
    logger.info(f'hostname: {hostname}')
    code_path = os.path.join(save_path,code_folder)
    
    action_info.save_path = save_path
    action_info.code_path = code_path
    action_info.scripts_path = os.path.join(code_path, run_folder)
    action_info.source_modified_flag = source_modified_flag
    action_info.version_data = version_data
    action_info.action_number = action # not i! 
    action_info.hostname = hostname

    os.makedirs(action_info.code_path, exist_ok=True)
    os.makedirs(action_info.scripts_path, exist_ok=True)
    
    # copy all code to task folder
    # assumes 'src' is named the same as the project name
    os.system(f'cp -r * {action_info.code_path}')   
    
    deploy(deploy_task, action_info, i, 'tasks', parent) # need to make these dependent on previous action



def get_param(i, parent):
    q = copy.deepcopy(parent)
    parts = []
    u = q
    for k, item in zip(i, ['actions', 'tasks', 'runs']):
        u = u.__dict__[item][k]
        parts.append(u)
        
    u = q
    for part,item in zip(parts,['actions', 'tasks', 'runs']):
        setattr(u, item, [part,])
        u = part
    
    return q

def deploy_task(task_info, i, parent):
    
    task_id = i[-1]
    task_info.__name__ = 'task'
    file_ = f"{task_id}"
    if task_info.task_name:
        file += f'-{task_info.task_name}'
    task_info.task_path = os.path.join(task_info.save_path, file_)
    os.makedirs(task_info.task_path, exist_ok=True)
    with open(os.path.join(task_info.task_path,'readme.md'), 'w') as f:
        f.write(task_info.__dict__.get('description', ''))
        
    param = get_param(i, parent)
    
    deploy(deploy_run, task_info, i, 'runs', param)           


def deploy_run(run_info, _id, system):
    # now start each run
   
    run_info.action_id, run_info.task_id, run_info.run_id = _id
    action = system.actions[_id[0]]
    run_info.__name__ = 'run'
    run_info.version = action.version_data['version']
    run_info._id = _id
    run_info.job_name = f'{system.project_name}-v{".".join([str(s) for s in run_info.version])}-{action.action_number}.{run_info.task_id}.{run_info.run_id}'

    run_info.save_path = os.path.join(run_info.task_path, str(run_info.run_id))
    os.makedirs(run_info.save_path, exist_ok=True)
    
    with open(run_info.save_path + '/' + run_info_file, 'w') as f:
        f.write(str(system))

    serialize_class(system, run_info.save_path + '/' + run_info_file)

    os.environ['save_path'] = run_info.save_path
    logfile = f'{run_info.save_path}/.log'
    
    
    with Bash(sg_engine(system.run, run_info,
                        pylogfile=logfile.replace('.log', '_python.log'),
                        logfile=logfile.replace('.log', '_engine.log')),
              path=run_info.save_path):
        
        wifi = check_wifi()
        
        if not wifi:
            os.environ["WANDB_MODE"] = "offline" # disable wandb sync  
        
        if action.no_compute or (action.hostname != system.cluster_name):
            tasklogger.info('Starting local task...')
            os.system(f'source {sg_engine_filename}')
        else:
            tasklogger.info('Starting cluster task...')
            os.system(f'qsub {sg_engine_filename}')
        
            if not wifi:
                tasklogger.info('Starting services...')
                # os.system(f"tmux kill-session -t {run_info.project_name}-services")
                # os.system(f"tmux new -A -d -s {run_info.project_name}-services 'python3 src/auto/services/service_tmux.py; $SHELL'")  
        
    #     tasklogger.info('Task submitted.')
            
### add to a queue and run actions serially 
### run tasks in parallel

# Problem with sg-queue is that GPUs are not exclusive etc...
# but you can cancel jobs though...

# so use sg-queue with smart GPU allocation on backend
# and then run tasks in parallel per action...with delayed task start to get correct gpu
# alternatively, use a queue system that has GPU exclusivity built in...