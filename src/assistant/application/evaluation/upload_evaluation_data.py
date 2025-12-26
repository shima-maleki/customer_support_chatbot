import json
from pathlib import Path

import opik

from assistant.infrastructure import opik_utils


def upload_dataset(name: str, data_path: Path) -> opik.Dataset:
    assert data_path.exists(), f"File {data_path} does not exist."

    with open(data_path, "r") as f:
        evaluation_data = json.load(f)


    dataset = opik_utils.create_dataset(
        name=name,
        description="Dataset containing question-answer pairs.",
        items=evaluation_data,
    )

    return dataset