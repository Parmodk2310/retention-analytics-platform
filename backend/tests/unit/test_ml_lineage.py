import json

from app.ml import lineage


def test_archive_latest_artifacts(
    tmp_path,
    monkeypatch,
) -> None:
    model_path = tmp_path / lineage.MODEL_FILENAME

    metadata_path = tmp_path / lineage.METADATA_FILENAME

    model_path.write_bytes(b"model-data")

    metadata_path.write_text(
        json.dumps({"model_version": "churn_test_v1"}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        lineage.settings,
        "MODEL_ARTIFACT_DIR",
        tmp_path,
    )

    result = lineage.archive_latest_artifacts()

    version_dir = tmp_path / "versions" / "churn_test_v1"

    assert (version_dir / lineage.MODEL_FILENAME).exists()

    assert (version_dir / lineage.METADATA_FILENAME).exists()

    assert result["model_version"] == "churn_test_v1"
