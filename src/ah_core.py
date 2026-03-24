import numpy as np
from scipy.signal import welch
from typing import Literal, Optional


def compute_tau(
    signal: np.ndarray,
    fs: float = 1.0,
    method: Literal["autocorr_decay", "spectral_width"] = "spectral_width",
    threshold: float = 1 / np.e,
    nperseg: Optional[int] = None,
) -> float:
    """
    Memory horizon τ for any 1-D signal.
    Used in: §W p=0.0008, §EQ p=0.0000, §EP p=0.0000,
             §C3 p=0.0000, §SA p=0.00019, §DM p=0.032
    """
    x = np.asarray(signal, dtype=float).ravel()
    n = len(x)
    if n < 20:
        return np.nan
    x = x - x.mean()
    if x.std() < 1e-12:
        return np.nan

    if method == "spectral_width":
        seg = nperseg or min(256, n // 4)
        seg = max(seg, 8)
        freq, psd = welch(x, fs=fs, nperseg=seg)
        if psd.max() == 0:
            return np.nan
        psd_norm = psd / psd.max()
        half = psd_norm >= 0.5
        if half.sum() < 2:
            half = psd_norm >= (1 / np.e)
        if half.sum() < 2:
            return np.nan
        idx = np.where(half)[0]
        fwhm = freq[idx[-1]] - freq[idx[0]]
        return (1.0 / fwhm) if fwhm > 1e-12 else np.nan

    elif method == "autocorr_decay":
        ac = np.correlate(x, x, mode="full")
        ac = ac[n - 1:]
        ac = ac / ac[0]
        below = np.where(ac < threshold)[0]
        if len(below) == 0:
            return (n - 1) / fs
        return float(below[0]) / fs

    else:
        raise ValueError(f"Unknown method '{method}'")


def compute_tau_series(
    signal: np.ndarray,
    window: int,
    step: int = 1,
    fs: float = 1.0,
    method: str = "spectral_width",
) -> np.ndarray:
    """Sliding-window τ series. Drop = approaching phase transition."""
    out = []
    for start in range(0, len(signal) - window, step):
        out.append(compute_tau(signal[start:start+window], fs=fs, method=method))
    return np.array(out)


def compute_ah(
    R: float, P: float, T: float, F: float, tau: float, k: float = 1.0,
) -> float:
    """Ah = (R·P·T·F)^(1/4). Any parameter=0 kills Ah."""
    if min(R, P, T, F) < 0:
        raise ValueError("All parameters must be non-negative.")
    return float((R * P * T * F) ** 0.25
