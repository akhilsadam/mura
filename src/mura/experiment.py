"""Task registry and dispatcher for multi-task training."""
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from omegaconf import DictConfig

from .registry import Registry


@dataclass
class TaskConfig:
    """Configuration for a task handler."""

    name: str
    handler: Callable[[DictConfig], Any]
    description: str = ""


# Global task registry
TASK_REGISTRY = Registry[Callable](name="TaskRegistry")


def run_task(cfg: DictConfig) -> Any:
    """Dispatch to task handler based on cfg.task."""
    task_name = cfg.get("task", "train_ae")

    if task_name not in TASK_REGISTRY:
        available = ", ".join(TASK_REGISTRY.list_all())
        raise ValueError(
            f"Unknown task '{task_name}'. Available: {available}\n"
            f"Set 'task' in config. Example: task: train_diffusion"
        )

    handler = TASK_REGISTRY.get(task_name)
    return handler(cfg)


def register_task(name: str, handler: Callable[[DictConfig], Any], description: str = "") -> None:
    """Register a task handler."""
    TASK_REGISTRY.register(name, TaskConfig, lambda cfg=None: handler)
