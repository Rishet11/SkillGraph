from __future__ import annotations

from .explanations import build_summary
from .graph import build_graph_payload
from .parser import ParsedDocument
from .recommendations import build_learning_path
from .scoring import compare_skills, score_resume_skills
from .schemas import AnalyzeResponse, ParseMetadata
from .skills import extract_skill_evidence, infer_target_importance


def analyze_documents(resume: ParsedDocument, job_description: ParsedDocument) -> AnalyzeResponse:
    resume_evidence = extract_skill_evidence(resume.text)
    scored_resume_skills = score_resume_skills(resume_evidence)
    target_skills = infer_target_importance(job_description.text)
    matched, missing, fit_score, confidence = compare_skills(scored_resume_skills, target_skills)
    learning_path = build_learning_path(missing)
    graph = build_graph_payload(scored_resume_skills, target_skills, missing, learning_path)
    warnings = list(dict.fromkeys([*resume.warnings, *job_description.warnings]))
    return AnalyzeResponse(
        fit_score=fit_score,
        confidence=confidence,
        resume_skills=scored_resume_skills,
        target_skills=target_skills,
        matched_skills=matched,
        missing_skills=missing,
        graph=graph,
        learning_path=learning_path,
        summary=build_summary(fit_score, matched, missing),
        warnings=warnings,
        parse_metadata={
            "resume": ParseMetadata(
                source=resume.source,
                filename=resume.filename,
                characters=len(resume.text),
                warnings=resume.warnings,
            ),
            "job_description": ParseMetadata(
                source=job_description.source,
                filename=job_description.filename,
                characters=len(job_description.text),
                warnings=job_description.warnings,
            ),
        },
    )

