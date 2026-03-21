from __future__ import annotations

from .courses import recommend_course
from .confidence import apply_adjusters
from .data_loader import Domain, load_skills
from .graph import (
    build_gap_subgraph,
    build_graph_payload,
    build_learning_subgraph,
    build_skill_graph,
    compute_gap_report,
    generate_learning_path,
    identify_gaps,
)
from .mastery import compute_mastery_scores
from .parser import ParsedDocument
from .reasoning import generate_trace
from .schemas import AnalyzeResponse, AnalyzeSummary, GapReport, JDData, Metrics, ParseMetadata, ParseResponse, PathwayResponse
from .skills import classify_jd, classify_resume_skills

API_VERSION = "v1"


def run_parse(domain: Domain, resume: ParsedDocument, jd: ParsedDocument) -> ParseResponse:
    resume_skills = classify_resume_skills(resume.text, domain, resume.sections)
    jd_data = classify_jd(jd.text, domain, jd.sections)
    mastery_scores = compute_mastery_scores(load_skills(domain), resume_skills, jd_data)
    mastery_scores, adjuster_notes = apply_adjusters(mastery_scores, domain, resume_skills, jd_data)
    resume_warnings = list(resume.warnings)
    jd_warnings = [*jd.warnings, *adjuster_notes]
    if not resume_skills:
        resume_warnings.append("No skills were extracted from the resume. Add clearer skill bullets or use paste text.")
    if not jd_data.required and not jd_data.preferred:
        jd_warnings.append("No JD skills were detected. Include explicit requirements/preferred sections for better matching.")
    return ParseResponse(
        api_version=API_VERSION,
        domain=domain,
        resume_skills=resume_skills,
        jd_data=jd_data,
        mastery_scores=mastery_scores,
        parse_metadata={
            "resume": ParseMetadata(
                source=resume.source,
                filename=resume.filename,
                characters=len(resume.text),
                warnings=resume_warnings,
                extraction_method=resume.extraction_method,
                sections_detected=sorted((resume.sections or {}).keys()),
                section_character_counts={
                    section: len(content)
                    for section, content in (resume.sections or {}).items()
                },
            ),
            "jd": ParseMetadata(
                source=jd.source,
                filename=jd.filename,
                characters=len(jd.text),
                warnings=jd_warnings,
                extraction_method=jd.extraction_method,
                sections_detected=sorted((jd.sections or {}).keys()),
                section_character_counts={
                    section: len(content)
                    for section, content in (jd.sections or {}).items()
                },
            ),
        },
    )


def run_pathway(domain: Domain, resume_skills: list[dict], jd_data: JDData, mastery_scores: dict[str, float]) -> PathwayResponse:
    all_skills = load_skills(domain)
    graph = build_skill_graph(domain)
    resume_skill_index = {item.get("skill"): item for item in resume_skills}
    gap_report_data = compute_gap_report(mastery_scores, jd_data)
    gap_report = GapReport(**gap_report_data)
    gap_skills = identify_gaps(all_skills, mastery_scores, jd_data)
    gap_skills.update(gap_report.missing)
    gap_skills.update(gap_report.weak)
    gap_subgraph = build_gap_subgraph(graph, gap_skills)
    from .ranker import rank_skills
    priorities = rank_skills(list(gap_subgraph.nodes), domain, jd_data, mastery_scores, gap_subgraph)
    learning_subgraph = build_learning_subgraph(gap_subgraph, mastery_scores)
    path = generate_learning_path(learning_subgraph, priorities, mastery_scores)
    course_map = {skill: recommend_course(skill, gap_skills, domain) for skill in path}
    reasoning = [
        generate_trace(
            skill,
            index,
            gap_subgraph,
            priorities,
            mastery_scores,
            jd_data,
            resume_skill_index.get(skill),
        )
        for index, skill in enumerate(path)
    ]
    graph_payload = build_graph_payload(gap_subgraph, path, mastery_scores, gap_skills)
    metrics = Metrics(
        redundant_modules_eliminated=max(0, round(((len(all_skills) - len(path)) / max(len(all_skills), 1)) * 100)),
        naive_path_length=len(all_skills),
        recommended_path_length=len(path),
        reasoning_trace_coverage=100 if len(reasoning) == len(path) else 0,
    )
    return PathwayResponse(
        api_version=API_VERSION,
        path=path,
        reasoning=reasoning,
        course_map=course_map,
        mastery_scores=mastery_scores,
        gap_count=len(gap_skills),
        gap_skills=sorted(gap_skills),
        gap_report=gap_report,
        domain=domain,
        graph=graph_payload,
        metrics=metrics,
    )


def analyze_documents(domain: Domain, resume: ParsedDocument, jd: ParsedDocument) -> AnalyzeResponse:
    parsed = run_parse(domain, resume, jd)
    pathway = run_pathway(
        domain,
        [item.model_dump() for item in parsed.resume_skills],
        parsed.jd_data,
        parsed.mastery_scores,
    )
    parse_metadata = parsed.parse_metadata or {}
    resume_meta = parse_metadata.get("resume")
    jd_meta = parse_metadata.get("jd")
    warnings = [
        *(resume_meta.warnings if resume_meta else []),
        *(jd_meta.warnings if jd_meta else []),
    ]
    headline = "Path is ready for onboarding"
    if pathway.gap_count >= 8:
        headline = "Large role gap with clear dependency path"
    elif pathway.gap_count >= 4:
        headline = "Moderate skill gap with focused ramp plan"
    return AnalyzeResponse(
        api_version=API_VERSION,
        domain=domain,
        all_skills=load_skills(domain),
        resume_skills=parsed.resume_skills,
        jd_data=parsed.jd_data,
        mastery_scores=pathway.mastery_scores,
        path=pathway.path,
        reasoning=pathway.reasoning,
        course_map=pathway.course_map,
        gap_count=pathway.gap_count,
        gap_skills=pathway.gap_skills,
        gap_report=pathway.gap_report,
        graph=pathway.graph,
        metrics=pathway.metrics,
        parse_metadata=parse_metadata,
        summary=AnalyzeSummary(
            headline=headline,
            explanation=(
                f"SkillGraph found {pathway.gap_count} gaps in the {domain.upper()} domain "
                f"and generated a deterministic, dependency-aware path of {len(pathway.path)} steps."
            ),
        ),
        warnings=list(dict.fromkeys(warnings)),
    )
