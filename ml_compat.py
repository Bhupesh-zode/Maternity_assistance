"""
Load ML pickles saved with scikit-learn 1.2.x on newer sklearn runtimes.

Pickles were trained/exported with sklearn 1.2.1. Python 3.13+ often installs
sklearn 1.3+ where OrdinalEncoder expects _infrequent_enabled on transform().
"""

from pickle import load
from pathlib import Path

from django.conf import settings


def patch_sklearn_encoder_compat(estimator):
    """OrdinalEncoder pickles from sklearn 1.2.x miss attrs used in 1.3+."""
    if hasattr(estimator, "categories_") and not hasattr(estimator, "_infrequent_enabled"):
        estimator._infrequent_enabled = False
    return estimator


def load_sklearn_pickle(filename):
    path = Path(settings.BASE_DIR) / filename
    with path.open("rb") as f:
        obj = load(f)
    return patch_sklearn_encoder_compat(obj)
