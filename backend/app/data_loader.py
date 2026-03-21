from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal


Domain = str

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def load_skills(domain: Domain) -> list[str]:
    if domain == "swe":
        return _read_json(DATA_DIR / "skills_swe.json")
    elif domain == "data":
        return _read_json(DATA_DIR / "skills_data.json")
    elif domain == "hr":
        return _read_json(DATA_DIR / "skills_hr.json")
    return []  # V2 Upgrade: Return empty for JIT Universal Discovery


@lru_cache(maxsize=1)
def load_edges(domain: Domain) -> list[tuple[str, str]]:
    if domain == "swe":
        data = _read_json(DATA_DIR / "edges_swe.json")
    elif domain == "data":
        data = _read_json(DATA_DIR / "edges_data.json")
    elif domain == "hr":
        data = _read_json(DATA_DIR / "edges_hr.json")
    else:
        return []
    return [tuple(item) for item in data]


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

