import os
from jinja2 import Environment, FileSystemLoader

from mura.util import localpath

env = Environment(loader=FileSystemLoader(localpath('templates/')),comment_start_string='###',line_statement_prefix = '###',line_comment_prefix='###')

script_folder = 'auto/tmp'
sg_engine_filename = 'auto/tmp/sg_engine.sh'
os.makedirs(script_folder, exist_ok=True)

def sg_engine(run, runinfo, **kwargs):
    template = env.get_template(run.submit_template)
    _init = env.get_template(run.env_init_template).render(
        install=run.install_info,
        **kwargs)
    _end = env.get_template(run.env_end_template).render(**kwargs)
    atr_id = runinfo._id
    single_run = env.get_template(run.run_template).render(
        env_init_commands=_init,
        env_end_commands=_end,
        runner = runinfo.runner,
        version = '.'.join([str(s) for s in runinfo.version]),
        a_index = atr_id[0],
        t_index = atr_id[1],
        r_index = atr_id[2],
        configfile = run.param_file,
        **kwargs)  
    return template.render(**kwargs,
                           run_commands=single_run,
                           jobname = runinfo.job_name,
                           )

def write_script(filename, script):
    os.makedirs(script_folder, exist_ok=True)
    with open(filename, 'w') as f:
        f.write(script)
    os.system(f'chmod +x {filename}')

class Bash():
    def __init__(self, script, path='.', delete=False, **kwargs):
        self.filename = sg_engine_filename
        self.script = script
        self.delete = delete
        self.path = path
        self.kwargs = kwargs
    def __enter__(self):
        write_script(self.filename, self.script)
        # cp script to path
        os.system(f'cp {self.filename} {self.path}')
        
    
    def __exit__(self, *args, **kwargs):
        if self.delete:
            sleep(4)
            self.delete_script()
    
    def delete_script(self):
        assert self.filename is not None
        assert os.path.exists(self.filename)
        assert self.filename.contains('/tmp/')
        os.system(f'rm {self.filename}')