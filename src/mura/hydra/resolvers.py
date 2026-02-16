"""OmegaConf resolvers for Hydra configs.

Provides custom resolvers for:
- Git information (SHA, dirty status, commit messages)
- Time-based unique IDs
- Other utilities
"""

import datetime
from typing import Dict, Any
from omegaconf import OmegaConf
import git


def generate_sec_id() -> str:
    """Generate compact base36 timestamp ID (unique, sortable, 6 chars)."""
    dt = datetime.datetime.now()
    epoch = datetime.datetime(2025, 1, 1)
    delta = int((dt - epoch).total_seconds())
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s = ""
    while delta:
        delta, i = divmod(delta, 36)
        s = chars[i] + s
    return s or "0"


def compute_git_info() -> Dict[str, Any]:
    """Calculate git information including diff summary.
    
    Returns:
        Dictionary with keys: sha, dirty, diff_text, long_msg, short_msg
    """
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        dirty = repo.is_dirty()

        if dirty:
            diff = repo.git.diff()
        else:
            # diff to last commit
            diff = repo.git.diff(f"{sha}~1", sha)

        # Try to summarize with LLM if available
        try:
            from ..util import llm
            summary, short_sum = llm.summarize_diff(diff)
        except Exception:
            summary = ""
            short_sum = ""
            
        return {
            'sha': sha,
            'dirty': dirty,
            'diff_text': diff,
            'long_msg': summary,
            'short_msg': short_sum,
        }
    except Exception as e:
        print(f"Warning: Git info computation failed: {e}")
        return {
            'sha': 'unknown',
            'dirty': False,
            'diff_text': '',
            'long_msg': '',
            'short_msg': '',
        }


# Global cache for git info (computed once at startup)
_GIT_INFO_CACHE = None


def _get_git_info() -> Dict[str, Any]:
    """Get cached git info."""
    global _GIT_INFO_CACHE
    if _GIT_INFO_CACHE is None:
        _GIT_INFO_CACHE = compute_git_info()
    return _GIT_INFO_CACHE


def _gitinfo_resolver(key: str) -> str:
    """OmegaConf resolver for git information."""
    info = _get_git_info()
    return str(info.get(key, ''))


def _sec_id_resolver() -> str:
    """OmegaConf resolver for sec_id."""
    return generate_sec_id()


def register_resolvers() -> None:
    """Register all custom OmegaConf resolvers.
    
    Call this once at module level in your training script:
        from mura.hydra import register_resolvers
        register_resolvers()
    
    Then use in configs:
        git:
          sha: ${gitinfo:sha}
          dirty: ${gitinfo:dirty}
          short_msg: ${gitinfo:short_msg}
        
        run_id: ${sec_id:}
    """
    # Register gitinfo resolver (supports keys: sha, dirty, long_msg, short_msg)
    OmegaConf.register_new_resolver("gitinfo", _gitinfo_resolver, replace=True)
    
    # Register sec_id resolver
    OmegaConf.register_new_resolver("sec_id", _sec_id_resolver, replace=True)
    
    print("Mura resolvers registered (gitinfo, sec_id)")
