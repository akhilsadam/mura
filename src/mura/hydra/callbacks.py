"""PyTorch Lightning callbacks for Hydra-based training.

Provides enhanced callbacks for:
- Git tracking and diff logging
- Version tracking across runs
- Artifact management
"""

import hashlib
import os
from pathlib import Path
from typing import Optional

import git
from lightning.pytorch.callbacks import Callback
from lightning.pytorch.utilities import rank_zero_only


class EnhancedGitCallback(Callback):
    """Enhanced git tracking callback.
    
    Logs to WandB:
    - Commit hash
    - Branch name
    - Dirty status
    - Diff SHA256 hash
    
    Saves to artifacts:
    - git_diff.patch (if repo is dirty)
    """
    
    @rank_zero_only
    def on_fit_start(self, trainer, pl_module):
        try:
            repo = git.Repo(search_parent_directories=True)
            commit_hash = repo.head.commit.hexsha
            
            try:
                branch = repo.active_branch.name
            except TypeError:
                # Detached HEAD state
                branch = "detached"
            
            diff = repo.git.diff()
            diff_hash = hashlib.sha256(diff.encode()).hexdigest()
            dirty = bool(diff)
            
            # Log to WandB
            if trainer.logger:
                trainer.logger.experiment.config.update({
                    "git/commit": commit_hash,
                    "git/branch": branch,
                    "git/diff_sha256": diff_hash,
                    "git/dirty": dirty,
                })
                
            # Save diff to artifacts if dirty and we have a log directory
            if dirty and hasattr(trainer.logger, 'log_dir') and trainer.logger.log_dir:
                diff_path = Path(trainer.logger.log_dir).parent / "git_diff.patch"
                diff_path.write_text(diff)
                print(f"Saved git diff to {diff_path}")
                
        except Exception as e:
            print(f"Git tracking failed: {str(e)}")


class VersionTrackerCallback(Callback):
    """Version tracking callback (lightweight).
    
    Logs version information to WandB config.
    """
    
    def __init__(self, version_id: Optional[str] = None):
        """
        Args:
            version_id: Optional version identifier (e.g., from sec_id)
        """
        super().__init__()
        self.version_id = version_id
    
    @rank_zero_only
    def on_fit_start(self, trainer, pl_module):
        if trainer.logger and self.version_id:
            trainer.logger.experiment.config.update({
                "version/run_id": self.version_id,
            })
