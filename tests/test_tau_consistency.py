import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from ah_core import compute_tau, compute_ah

def test_broadband_vs_narrow():
    broad  = np.random.randn(512)
    t      = np.arange(512)
    narrow = np.sin(2*np.pi*0.1*t) + 0.05*np.random.randn(512)
    assert compute_tau(narrow) > compute_tau(broad)

def test_nan_on_constant():
    assert np.isnan(compute_tau(np.ones(100)))

def test_ah_zero_kills():
    assert compute_ah(0, 1, 1, 1, tau=1) == 0.0

def test_ah_balanced():
    assert abs(compute_ah(0.5, 0.5, 0.5, 0.5, tau=1) - 0.5) < 0.001
