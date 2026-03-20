from __future__ import annotations

from .skills import llm_enrichment_enabled


def build_summary(fit_score: int, matched_skills, missing_skills):
    if fit_score >= 75:
        headline = "Strong role alignment"
    elif fit_score >= 50:
        headline = "Promising fit with a few onboarding gaps"
    else:
        headline = "Needs a structured ramp-up plan"
    explanation = (
        f"The candidate matches {len(matched_skills)} role skills and has "
        f"{len(missing_skills)} notable gaps. Scores are deterministic and traceable to extracted evidence."
    )
    if llm_enrichment_enabled():
        explanation += " LLM enrichment is enabled for wording only; the scoring logic remains deterministic."
    return {"headline": headline, "explanation": explanation}

