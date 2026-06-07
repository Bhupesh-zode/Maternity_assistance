"""Retrain GradientBoostingClassifier.pkl for the current scikit-learn version."""

from pathlib import Path
from pickle import dump

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from sklearn.ensemble import GradientBoostingClassifier

from ml_compat import load_sklearn_pickle


class Command(BaseCommand):
    help = (
        "Retrain GradientBoostingClassifier.pkl from dataset/childbirth2.csv. "
        "Run after upgrading scikit-learn when the old pickle fails to load."
    )

    def handle(self, *args, **options):
        csv_path = Path(settings.BASE_DIR) / "dataset" / "childbirth2.csv"
        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f"Dataset not found: {csv_path}"))
            raise SystemExit(1)

        df = pd.read_csv(csv_path)
        df["NUMBER OF PREV CESAREAN"] = df["NUMBER OF PREV CESAREAN"].astype("object")

        encoder = load_sklearn_pickle("encoder.pkl")
        y_encoder = load_sklearn_pickle("y_encoder.pkl")
        X = encoder.transform(df.drop(["TYPE OF BIRTH    "], axis=1))
        Y = y_encoder.transform(df[["TYPE OF BIRTH    "]]).ravel()

        model = GradientBoostingClassifier(random_state=0)
        model.fit(X, Y)

        out_path = Path(settings.BASE_DIR) / "GradientBoostingClassifier.pkl"
        with out_path.open("wb") as f:
            dump(model, f)

        load_sklearn_pickle("GradientBoostingClassifier.pkl")
        self.stdout.write(
            self.style.SUCCESS(f"Retrained and saved {out_path.name} ({len(df)} rows).")
        )
