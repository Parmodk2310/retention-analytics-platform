from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TemporalSplits:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def temporal_train_validation_test_split(
    df: pd.DataFrame,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
) -> TemporalSplits:
    """
    Split complete snapshot dates chronologically.

    Snapshot dates are never divided across datasets and no random
    row-level split is used.
    """
    if "snapshot_date" not in df.columns:
        raise ValueError("Dataset must contain snapshot_date.")

    if df.empty:
        raise ValueError("Cannot split an empty dataset.")

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")

    if not 0 < validation_fraction < 1:
        raise ValueError("validation_fraction must be between 0 and 1.")

    if train_fraction + validation_fraction >= 1:
        raise ValueError("train_fraction + validation_fraction must leave data for testing.")

    snapshot_dates = sorted(pd.to_datetime(df["snapshot_date"]).dt.normalize().unique())

    n_dates = len(snapshot_dates)

    if n_dates < 3:
        raise ValueError(
            "At least three distinct snapshot dates are required for "
            "train/validation/test splitting."
        )

    train_count = max(1, int(n_dates * train_fraction))
    validation_count = max(1, int(n_dates * validation_fraction))

    # Always reserve at least one complete snapshot for final testing.
    if train_count + validation_count >= n_dates:
        validation_count = 1
        train_count = n_dates - 2

    train_dates = set(snapshot_dates[:train_count])

    validation_start = train_count
    validation_end = train_count + validation_count

    validation_dates = set(snapshot_dates[validation_start:validation_end])

    test_dates = set(snapshot_dates[validation_end:])

    normalized = pd.to_datetime(df["snapshot_date"]).dt.normalize()

    train = df.loc[normalized.isin(train_dates)].copy()
    validation = df.loc[normalized.isin(validation_dates)].copy()
    test = df.loc[normalized.isin(test_dates)].copy()

    if train.empty or validation.empty or test.empty:
        raise RuntimeError("Temporal split produced an empty train, validation, or test set.")

    if train["snapshot_date"].max() >= validation["snapshot_date"].min():
        raise RuntimeError("Training and validation periods overlap.")

    if validation["snapshot_date"].max() >= test["snapshot_date"].min():
        raise RuntimeError("Validation and test periods overlap.")

    return TemporalSplits(
        train=train,
        validation=validation,
        test=test,
    )


def split_metadata(splits: TemporalSplits) -> dict:
    def describe(frame: pd.DataFrame) -> dict:
        return {
            "rows": int(len(frame)),
            "snapshot_count": int(frame["snapshot_date"].nunique()),
            "start": frame["snapshot_date"].min().date().isoformat(),
            "end": frame["snapshot_date"].max().date().isoformat(),
            "churn_rate": float(frame["churned"].mean()),
        }

    return {
        "train": describe(splits.train),
        "validation": describe(splits.validation),
        "test": describe(splits.test),
    }


@dataclass(frozen=True)
class FitCalibrationSplit:
    fit: pd.DataFrame
    calibration: pd.DataFrame


def temporal_fit_calibration_split(
    train_df: pd.DataFrame,
) -> FitCalibrationSplit:
    """
    Reserve the latest training snapshot for
    probability calibration.
    """

    frame = train_df.copy()

    dates = pd.to_datetime(frame["snapshot_date"]).dt.normalize()

    unique_dates = sorted(dates.unique())

    if len(unique_dates) < 2:
        raise RuntimeError("At least two training snapshots are required for calibration.")

    calibration_date = unique_dates[-1]

    fit = frame[dates < calibration_date].copy()

    calibration = frame[dates == calibration_date].copy()

    if fit.empty or calibration.empty:
        raise RuntimeError("Temporal calibration split produced an empty partition.")

    return FitCalibrationSplit(
        fit=fit,
        calibration=calibration,
    )
