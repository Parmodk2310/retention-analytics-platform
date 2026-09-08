import json
import shutil
from pathlib import Path

from app.core.config import settings


MODEL_FILENAME = "churn_model.joblib"
METADATA_FILENAME = "model_metadata.json"


def archive_latest_artifacts() -> dict[str, str]:
    """
    Copy the current accepted model and metadata into
    a version-specific local artifact directory.

    This operation is idempotent.
    """

    artifact_root = Path(settings.MODEL_ARTIFACT_DIR)

    model_path = artifact_root / MODEL_FILENAME

    metadata_path = artifact_root / METADATA_FILENAME

    if not model_path.exists():
        raise FileNotFoundError(model_path)

    if not metadata_path.exists():
        raise FileNotFoundError(metadata_path)

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    model_version = metadata.get("model_version")

    if not model_version:
        raise RuntimeError("Model metadata does not contain model_version.")

    version_directory = artifact_root / "versions" / model_version

    version_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    version_model_path = version_directory / MODEL_FILENAME

    version_metadata_path = version_directory / METADATA_FILENAME

    shutil.copy2(
        model_path,
        version_model_path,
    )

    shutil.copy2(
        metadata_path,
        version_metadata_path,
    )

    return {
        "model_version": model_version,
        "model_path": str(version_model_path),
        "metadata_path": str(version_metadata_path),
    }


if __name__ == "__main__":
    print(
        json.dumps(
            archive_latest_artifacts(),
            indent=2,
        )
    )
