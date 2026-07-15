"""Quick tests for Phase 0 mura additions."""
import pytest
import torch
from omegaconf import DictConfig, OmegaConf

from mura.registry import Registry
from mura.experiment import TASK_REGISTRY, run_task
from mura.checkpointing import save_checkpoint, load_checkpoint
from mura.metrics import compute_psnr, compute_ssim, compute_l2, aggregate_metrics


def test_registry_basic():
    """Test basic registry functionality."""
    reg = Registry[str](name="TestRegistry")

    # Mock config and builder
    class MockConfig:
        pass

    def builder(cfg):
        return "test_object"

    reg.register("test_key", MockConfig, builder)

    assert "test_key" in reg
    assert "test_key" in reg.list_all()
    assert reg.get("test_key") == builder


def test_registry_duplicate_raises():
    """Test that duplicate registration raises."""
    reg = Registry[str](name="TestRegistry")

    class MockConfig:
        pass

    def builder(cfg):
        return "test"

    reg.register("key", MockConfig, builder)
    with pytest.raises(ValueError, match="already registered"):
        reg.register("key", MockConfig, builder)


def test_task_registry():
    """Test task registry and dispatcher."""
    # Clear and register a test task
    def test_handler(cfg: DictConfig):
        return cfg.value * 2

    TASK_REGISTRY.register("test_task", None, test_handler)
    assert "test_task" in TASK_REGISTRY

    cfg = OmegaConf.create({"task": "test_task", "value": 5})
    result = run_task(cfg)
    assert result == 10


def test_metrics():
    """Test metric computation."""
    # Create identical tensors
    x = torch.ones(2, 3, 64, 64)
    y = torch.ones(2, 3, 64, 64)

    psnr = compute_psnr(x, y)
    assert psnr == float("inf")  # Identical images = infinite PSNR

    ssim = compute_ssim(x, y)
    assert ssim == pytest.approx(1.0, abs=0.01)  # Identical images ≈ SSIM=1

    l2 = compute_l2(x, y)
    assert l2 == pytest.approx(0.0)

    # Test aggregation
    metrics = aggregate_metrics(x, y, ["psnr", "ssim", "l2"])
    assert "psnr" in metrics
    assert "ssim" in metrics
    assert "l2" in metrics


def test_metrics_different():
    """Test metrics with different tensors."""
    x = torch.ones(1, 3, 32, 32)
    y = torch.zeros(1, 3, 32, 32)

    psnr = compute_psnr(x, y, data_range=1.0)
    assert psnr > 0  # Should have measurable PSNR

    ssim = compute_ssim(x, y, data_range=1.0)
    assert 0 <= ssim <= 1  # SSIM should be in [0,1]

    l2 = compute_l2(x, y)
    assert l2 > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
