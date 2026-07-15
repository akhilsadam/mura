"""Generic metric computation and aggregation."""
from typing import Dict, Optional

import torch
import torch.nn.functional as F


def compute_psnr(pred: torch.Tensor, target: torch.Tensor, data_range: float = 1.0) -> float:
    """Compute PSNR between prediction and target.

    Args:
        pred: Predicted tensor, shape (B, C, H, W) or any shape
        target: Target tensor, same shape as pred
        data_range: Maximum possible value (default 1.0 for normalized [0,1])

    Returns:
        PSNR in dB
    """
    mse = F.mse_loss(pred, target)
    if mse == 0:
        return float("inf")
    psnr = 20 * torch.log10(data_range / torch.sqrt(mse))
    return float(psnr)


def compute_ssim(pred: torch.Tensor, target: torch.Tensor, data_range: float = 1.0, window_size: int = 11) -> float:
    """Compute SSIM between prediction and target.

    Simplified SSIM (2D only, for multi-dim tensors averages over spatial dims).

    Args:
        pred: Predicted tensor
        target: Target tensor
        data_range: Maximum possible value
        window_size: Gaussian window size

    Returns:
        SSIM score in [0, 1]
    """
    # Create Gaussian window
    x = torch.arange(window_size, dtype=torch.float32) - (window_size - 1) / 2.0
    gauss = torch.exp(-x.pow(2.0) / 2)
    kernel = gauss / gauss.sum()
    kernel = kernel.unsqueeze(0).unsqueeze(0)

    # Flatten to 2D if needed (B, C, H, W)
    if pred.dim() == 4:
        # Compute for each channel
        b, c, h, w = pred.shape
        pred_flat = pred.view(b * c, 1, h, w)
        target_flat = target.view(b * c, 1, h, w)
    else:
        pred_flat = pred.unsqueeze(0).unsqueeze(0) if pred.dim() == 2 else pred
        target_flat = target.unsqueeze(0).unsqueeze(0) if target.dim() == 2 else target

    kernel = kernel.to(pred_flat.device).expand(pred_flat.shape[1], -1, -1, -1)

    # Compute local means
    mu1 = F.conv2d(pred_flat, kernel, padding=window_size // 2, groups=pred_flat.shape[1])
    mu2 = F.conv2d(target_flat, kernel, padding=window_size // 2, groups=target_flat.shape[1])

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    # Compute local variances
    sigma1_sq = F.conv2d(pred_flat * pred_flat, kernel, padding=window_size // 2, groups=pred_flat.shape[1]) - mu1_sq
    sigma2_sq = F.conv2d(target_flat * target_flat, kernel, padding=window_size // 2, groups=target_flat.shape[1]) - mu2_sq
    sigma12 = F.conv2d(pred_flat * target_flat, kernel, padding=window_size // 2, groups=pred_flat.shape[1]) - mu1_mu2

    # SSIM formula
    c1 = (0.01 * data_range) ** 2
    c2 = (0.03 * data_range) ** 2

    ssim_map = ((2 * mu1_mu2 + c1) * (2 * sigma12 + c2)) / ((mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2))

    return float(ssim_map.mean())


def compute_l2(pred: torch.Tensor, target: torch.Tensor) -> float:
    """Compute L2 distance between prediction and target.

    Args:
        pred: Predicted tensor
        target: Target tensor

    Returns:
        L2 distance (Frobenius norm)
    """
    return float(torch.norm(pred - target, p=2))


def aggregate_metrics(
    predictions: torch.Tensor,
    targets: torch.Tensor,
    metric_names: list[str],
    data_range: float = 1.0,
) -> Dict[str, float]:
    """Compute multiple metrics at once.

    Args:
        predictions: Batch of predictions
        targets: Batch of targets
        metric_names: List of metric names ('psnr', 'ssim', 'l2')
        data_range: Data range for PSNR/SSIM

    Returns:
        Dict of metric_name -> value
    """
    results = {}

    for metric_name in metric_names:
        if metric_name.lower() == "psnr":
            results["psnr"] = compute_psnr(predictions, targets, data_range=data_range)
        elif metric_name.lower() == "ssim":
            results["ssim"] = compute_ssim(predictions, targets, data_range=data_range)
        elif metric_name.lower() == "l2":
            results["l2"] = compute_l2(predictions, targets)
        else:
            raise ValueError(f"Unknown metric: {metric_name}")

    return results
