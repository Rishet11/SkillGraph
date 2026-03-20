from __future__ import annotations

import os
import re
from collections import defaultdict

from .data_loader import load_skills


SECTION_HINTS = {
    "skills": "skills",
    "summary": "summary",
    "experience": "experience",
    "projects": "projects",
}


def build_skill_lookup():
    lookup: dict[str, dict] = {}
    for skill in load_skills():
        for alias in [skill["label"], *skill["aliases"]]:
            lookup[alias.lower()] = skill
    return lookup


def detect_sections(text: str) -> dict[str, str]:
    section = "general"
    sections: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lowered = line.lower().rstrip(":")
        if lowered in SECTION_HINTS:
            section = SECTION_HINTS[lowered]
            continue
        if line:
            sections[line] = section
    return sections


def extract_skill_evidence(text: str):
    lookup = build_skill_lookup()
    sections = detect_sections(text)
    evidence: dict[str, dict] = {}
    hits = defaultdict(int)
    lowered_text = text.lower()
    for alias, skill in lookup.items():
        if alias not in lowered_text:
            continue
        pattern = re.compile(rf"(.{{0,45}}{re.escape(alias)}.{{0,45}})", re.IGNORECASE)
        snippets = [match.group(1).strip() for match in pattern.finditer(text)][:3]
        section = "general"
        for original_line, line_section in sections.items():
            if alias in original_line.lower():
                section = line_section
                break
        hits[skill["id"]] += max(1, len(snippets))
        item = evidence.setdefault(
            skill["id"],
            {
                "skill_id": skill["id"],
                "label": skill["label"],
                "snippets": [],
                "source_section": section,
                "category": skill["category"],
            },
        )
        item["snippets"].extend(snippets or [skill["label"]])
        if section in {"skills", "summary", "experience"}:
            item["source_section"] = section
    results = []
    for skill_id, item in evidence.items():
        item["hits"] = hits[skill_id]
        item["snippets"] = list(dict.fromkeys(item["snippets"]))[:3]
        results.append(item)
    results.sort(key=lambda value: (-value["hits"], value["label"]))
    return results


def infer_target_importance(job_description_text: str):
    evidence = extract_skill_evidence(job_description_text)
    lines = [line.strip() for line in job_description_text.splitlines() if line.strip()]
    target_skills = []
    for item in evidence:
        skill_id = item["skill_id"]
        label = item["label"]
        importance = "preferred"
        for line in lines:
            lowered_line = line.lower()
            if label.lower() not in lowered_line:
                continue
            if any(keyword in lowered_line for keyword in ["bonus", "nice to have"]):
                importance = "bonus"
            elif any(keyword in lowered_line for keyword in ["preferred", "ideal candidate"]):
                importance = "preferred"
            elif any(keyword in lowered_line for keyword in ["required", "must have", "include"]):
                importance = "required"
        target_skills.append({"skill_id": skill_id, "label": label, "importance": importance})
    deduped = {}
    for skill in target_skills:
        current = deduped.get(skill["skill_id"])
        if not current or importance_rank(skill["importance"]) > importance_rank(current["importance"]):
            deduped[skill["skill_id"]] = skill
    return list(deduped.values())


def importance_rank(importance: str) -> int:
    order = {"bonus": 0, "preferred": 1, "required": 2}
    return order[importance]


def llm_enrichment_enabled() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) and os.getenv("SKILLGRAPH_ENABLE_LLM", "0") == "1"
