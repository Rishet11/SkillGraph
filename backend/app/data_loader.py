from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_skills():
    return _read_json(DATA_DIR / "skills.json")


@lru_cache(maxsize=1)
def load_edges():
    return _read_json(DATA_DIR / "edges.json")


@lru_cache(maxsize=1)
def load_courses():
    return _read_json(DATA_DIR / "courses.json")


@lru_cache(maxsize=1)
def load_weights():
    return _read_json(DATA_DIR / "weights.json")


@lru_cache(maxsize=1)
def load_samples():
    samples = []
    for path in sorted(SAMPLES_DIR.glob("*.txt")):
        kind = "resume" if "resume" in path.name else "job_description"
        samples.append(
            {
                "id": path.stem,
                "label": path.stem.replace("_", " ").title(),
                "type": kind,
                "content": path.read_text(encoding="utf-8"),
            }
        )
    return samples

