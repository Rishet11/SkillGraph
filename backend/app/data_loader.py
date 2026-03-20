from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal


Domain = Literal["swe", "data"]

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_skills(domain: Domain) -> list[str]:
    filename = "skills_swe.json" if domain == "swe" else "skills_data.json"
    return _read_json(DATA_DIR / filename)


@lru_cache(maxsize=1)
def load_edges(domain: Domain) -> list[tuple[str, str]]:
    filename = "edges_swe.json" if domain == "swe" else "edges_data.json"
    return [tuple(item) for item in _read_json(DATA_DIR / filename)]


@lru_cache(maxsize=1)
def load_courses(domain: Domain) -> list[dict]:
    catalog = _read_json(DATA_DIR / "courses.json")
    expected_domain = "SWE" if domain == "swe" else "Data"
    return [
        item
        for item in catalog
        if item["domain"] in {expected_domain, "SWE/Data"}
    ]


@lru_cache(maxsize=1)
def load_demo_scenarios() -> list[dict]:
    return _read_json(DATA_DIR / "demo_scenarios.json")


def get_demo_scenario(sample_id: str) -> dict | None:
    for item in load_demo_scenarios():
        if item["id"] == sample_id:
            return item
    return None

