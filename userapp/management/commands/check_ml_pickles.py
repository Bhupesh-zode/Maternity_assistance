"""Smoke-test that committed ML pickle files load on this environment."""

from django.core.management.base import BaseCommand

from ml_compat import load_sklearn_pickle


# Minimal row matching training column names (user predict form).
_SAMPLE_ROW = {
    "PREVIOUS CESAREAN": [" t                   "],
    "COMPLICATIONS": [" t                  "],
    "ROBSON GROUP": [" group 1     "],
    "ART MODE": [" FIV     "],
    "AMNIOCENTESIS": [" t                     "],
    "EPISIOTOMY": ["T"],
    "OBSTETRIC RISK": [" t                    "],
    "COMORBIDITY": [" t                "],
    "START  ANTENATAL CARRE": ["1º trimester"],
    "ART": [" t       "],
    "AMNIOTIC LIQUID": [" clear        "],
    "REPEATED MISCARRIAGES ": ["t"],
    "CARDIOTOCOGRAPHY  ": ["no"],
    "MATERNAL EDUCATION": ["Without studies"],
}

_REQUIRED = ("encoder_newf.pkl", "y_encoder.pkl", "XGB.pkl")
# Admin-only; GradientBoostingClassifier often fails on sklearn 1.3+ (internal module moves).
_OPTIONAL = ("encoder.pkl", "GradientBoostingClassifier.pkl", "LogisticRegression.pkl")


class Command(BaseCommand):
    help = "Verify ML pickle files load and OrdinalEncoder transform works."

    def handle(self, *args, **options):
        import pandas as pd

        errors = []
        for name in _REQUIRED + _OPTIONAL:
            required = name in _REQUIRED
            try:
                load_sklearn_pickle(name)
                self.stdout.write(self.style.SUCCESS(f"OK  {name}"))
            except FileNotFoundError:
                msg = f"SKIP {name} (not found)"
                if required:
                    errors.append(f"{name}: missing")
                    self.stdout.write(self.style.ERROR(msg))
                else:
                    self.stdout.write(self.style.WARNING(msg))
            except Exception as exc:
                msg = f"{name}: {exc}"
                if required:
                    errors.append(msg)
                    self.stdout.write(self.style.ERROR(f"FAIL {msg}"))
                else:
                    self.stdout.write(self.style.WARNING(f"WARN {msg}"))

        encoder = load_sklearn_pickle("encoder_newf.pkl")
        df = pd.DataFrame(_SAMPLE_ROW)
        encoded = encoder.transform(df)
        if encoded.shape != (1, 14):
            errors.append(f"encoder_newf transform shape {encoded.shape}, expected (1, 14)")

        model = load_sklearn_pickle("XGB.pkl")
        y_encoder = load_sklearn_pickle("y_encoder.pkl")

        cols = list(_SAMPLE_ROW.keys())
        df_enc = pd.DataFrame(encoded, columns=cols)
        feature_row = {
            "PREVIOUS CESAREAN": df_enc["PREVIOUS CESAREAN"][0],
            "COMPLICATIONS": df_enc["COMPLICATIONS"][0],
            "ROBSON GROUP": df_enc["ROBSON GROUP"][0],
            "ART MODE": df_enc["ART MODE"][0],
            "AMNIOCENTESIS": df_enc["AMNIOCENTESIS"][0],
            "EPISIOTOMY": df_enc["EPISIOTOMY"][0],
            "PARITY": 2,
            "OBSTETRIC RISK": df_enc["OBSTETRIC RISK"][0],
            "COMORBIDITY": df_enc["COMORBIDITY"][0],
            "NUMBER OF PREV CESAREAN": 1,
            "KG INCREASED PREGNANCY": 12.0,
            "START  ANTENATAL CARRE": df_enc["START  ANTENATAL CARRE"][0],
            "ART": df_enc["ART"][0],
            "AMNIOTIC LIQUID": df_enc["AMNIOTIC LIQUID"][0],
            "REPEATED MISCARRIAGES ": df_enc["REPEATED MISCARRIAGES "][0],
            "GESTAGIONAL AGE ": 9,
            "HEIGHT": 175.0,
            "WEIGHT": 58.0,
            "BMI": 14.0,
            "AGE": 23,
            "CARDIOTOCOGRAPHY  ": df_enc["CARDIOTOCOGRAPHY  "][0],
            "MATERNAL EDUCATION": df_enc["MATERNAL EDUCATION"][0],
        }
        pred = model.predict(pd.DataFrame([feature_row]))
        label = y_encoder.inverse_transform(pred)[0]
        self.stdout.write(self.style.SUCCESS(f"OK  sample predict -> {label!r}"))

        if errors:
            self.stderr.write("\n".join(errors))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("All ML pickle checks passed."))
