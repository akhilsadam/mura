import os, yaml
import datetime
# ----------------------------
# Version Management Utilities
# ----------------------------
class VersionManager:
    def __init__(self, base_path: str = "./run"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
        self.version_file = os.path.join(self.base_path, "version.yaml")
        
    def load_version(self):
        if not os.path.exists(self.version_file):
            version_data = {
                'version': [0, 0],
                'run': 0
            }
            self.save_version(version_data)
            self.version_data = version_data
        else:
            with open(self.version_file, 'r') as f:
                self.version_data = yaml.safe_load(f)
                
        return self.version_data
    
    def save_version(self, version_data: dict):    
        with open(self.version_file, 'w') as f:
            yaml.safe_dump(version_data, f)
    
    def new_path(self, task_name, run_name):
        """Get next run directory path and update version"""
        version_data = self.load_version()
        run_number = version_data['run'] + 1
        version_data['run'] = run_number
        
        version = version_data['version']
        version[1] += 1
        
        run_path = os.path.join(self.base_path, f'{version[0]:05d}_{task_name}', f'{version[1]:05d}_{run_name}')
        os.makedirs(run_path, exist_ok=True)
        
        # Save updated version
        self.save_version(version_data)
        return run_path, run_number, version
    
    def finalize_run_info(self, run_path, config):
        """Save final run information to version file"""    
        self.version_data["completed_at"] = datetime.datetime.now().isoformat()
        self.version_data["run_path"] = str(run_path)
        
        # Add git info if available
        try:
            import git
            repo = git.Repo(search_parent_directories=True)
            self.version_data["git_commit"] = repo.head.commit.hexsha
            self.version_data["git_branch"] = repo.active_branch.name
        except Exception:
            pass

        # Save to run directory
        with open(os.path.join(run_path,"version_info.yaml"), "w") as f:
            yaml.safe_dump(self.version_data, f)