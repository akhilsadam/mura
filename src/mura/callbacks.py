import git
import hashlib
import os
from lightning.pytorch.callbacks import Callback
from lightning.pytorch.utilities import rank_zero_only

class GitTrackerCallback(Callback):
    @rank_zero_only
    def on_fit_start(self, trainer, pl_module):
        try:
            repo = git.Repo(search_parent_directories=True)
            commit_hash = repo.head.commit.hexsha
            branch = repo.active_branch.name
            diff = repo.git.diff()
            diff_hash = hashlib.sha256(diff.encode()).hexdigest()
            
            # Log to WandB
            if trainer.logger:
                trainer.logger.experiment.config.update({
                    "git/commit": commit_hash,
                    "git/branch": branch,
                    "git/diff_sha256": diff_hash,
                })
                
                # # Save diff as artifact
                # diff_path = f"diff_{commit_hash[:7]}.patch"
                # with open(diff_path, "w") as f:
                #     f.write(diff)
                
                # artifact = trainer.logger.experiment.Artifact(
                #     f"code-diff-{commit_hash[:7]}", 
                #     type="code-diff"
                # )
                # artifact.add_file(diff_path)
                # trainer.logger.experiment.log_artifact(artifact)
                # os.remove(diff_path)
                
        except Exception as e:
            print(f"Git tracking failed: {str(e)}")