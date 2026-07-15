"""Generic registry for models, datasets, solvers, operators, etc."""
from typing import Any, Callable, Dict, Generic, List, Optional, Type, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    """Generic registry for building objects from configs."""

    def __init__(self, name: str = "Registry"):
        self.name = name
        self._registry: Dict[str, tuple[Type, Callable]] = {}

    def register(self, key: str, config_cls: Type, builder: Callable) -> None:
        """Register an item: config class + builder function."""
        if key in self._registry:
            raise ValueError(f"Key '{key}' already registered in {self.name}")
        self._registry[key] = (config_cls, builder)

    def get(self, key: str) -> Callable:
        """Get builder function by key."""
        if key not in self._registry:
            available = ", ".join(self.list_all())
            raise KeyError(f"Unknown key '{key}' in {self.name}. Available: {available}")
        return self._registry[key][1]

    def get_config_cls(self, key: str) -> Type:
        """Get config class by key."""
        if key not in self._registry:
            available = ", ".join(self.list_all())
            raise KeyError(f"Unknown key '{key}' in {self.name}. Available: {available}")
        return self._registry[key][0]

    def list_all(self) -> List[str]:
        """List all registered keys."""
        return sorted(self._registry.keys())

    def __contains__(self, key: str) -> bool:
        """Check if key is registered."""
        return key in self._registry
