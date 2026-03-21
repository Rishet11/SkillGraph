from __future__ import annotations

from collections.abc import Callable

from .data_loader import Domain
from .schemas import JDData


Adjuster = Callable[
    [dict[str, float], Domain, list[dict], JDData],
    tuple[dict[str, float], list[str]],
]


_adjusters: list[Adjuster] = []


def register_adjuster(adjuster: Adjuster) -> None:
    _adjusters.append(adjuster)


def apply_adjusters(
    mastery_scores: dict[str, float],
    domain: Domain,
    resume_skills: list[dict],
    jd_data: JDData,
) -> tuple[dict[str, float], list[str]]:
    updated = dict(mastery_scores)
    notes: list[str] = []
    for adjuster in _adjusters:
        updated, adjuster_notes = adjuster(updated, domain, resume_skills, jd_data)
        if adjuster_notes:
            notes.extend(adjuster_notes)
    return updated, notes
