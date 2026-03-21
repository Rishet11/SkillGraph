from __future__ import annotations

from .courses import recommend_course
from .data_loader import Domain, load_skills
from .graph import (
    build_gap_subgraph,
    build_graph_payload,
    build_learning_subgraph,
    build_skill_graph,
    generate_learning_path,
    identify_gaps,
)
from .mastery import compute_mastery_scores
from .parser import ParsedDocument
from .reasoning import generate_trace
from .schemas import AnalyzeResponse, AnalyzeSummary, JDData, Metrics, ParseMetadata, ParseResponse, PathwayResponse
from .skills import classify_jd, classify_resume_skills
from .ontology import detect_industry


def get_mapped_domain(text: str) -> Domain:
    return detect_industry(text)


def run_parse(domain: Domain | None, resume: ParsedDocument, jd: ParsedDocument) -> ParseResponse:
    if domain is None:
        domain = get_mapped_domain(jd.text)
        
    resume_skills = classify_resume_skills(resume.text, domain)
    jd_data = classify_jd(jd.text, domain)
    mastery_scores = compute_mastery_scores(load_skills(domain), resume_skills, jd_data)
    return ParseResponse(
        domain=domain,
        resume_skills=resume_skills,
        jd_data=jd_data,
        mastery_scores=mastery_scores,
        parse_metadata={
            "resume": ParseMetadata(
                source=resume.source,
                filename=resume.filename,
                characters=len(resume.text),
                warnings=resume.warnings,
            ),
            "jd": ParseMetadata(
                source=jd.source,
                filename=jd.filename,
                characters=len(jd.text),
                warnings=jd.warnings,
            ),
        },
    )


def cluster_skills_into_pillars(skills: list[str]) -> dict[str, list[str]]:
    """Groups skills into logical high-level career pillars for dashboarding."""
    PILLARS = {
        "Core Engineering": ["Data Structures", "Algorithms", "OOP", "Testing", "Clean Code", "Design Patterns"],
        "Backend & Systems": ["Linux/CLI", "Operating Systems", "Computer Networks", "SQL", "REST APIs", "Node.js", "Databases (NoSQL)", "Microservices", "Caching (Redis)", "Message Queues", "System Design"],
        "Frontend & Web": ["HTML/CSS", "JavaScript", "TypeScript", "React", "GraphQL", "Git"],
        "DevOps & Cloud": ["Docker", "Cloud Basics", "CI/CD", "Security Basics"]
    }
    clusters = {p: [] for p in PILLARS}
    clusters["Other"] = []
    
    for skill in skills:
        found = False
        for pillar, skill_list in PILLARS.items():
            if skill in skill_list:
                clusters[pillar].append(skill)
                found = True
                break
        if not found:
            clusters["Other"].append(skill)
            
    return {p: s for p, s in clusters.items() if s}


def run_pathway(domain: Domain | None, resume_skills: list[dict], jd_data: JDData, mastery_scores: dict[str, float]) -> PathwayResponse:
    if domain is None:
        domain = "swe"
    all_skills = load_skills(domain)
    graph = build_skill_graph(domain)
    gap_skills = identify_gaps(all_skills, mastery_scores, jd_data)
    gap_subgraph = build_gap_subgraph(graph, gap_skills)
    from .ranker import rank_skills
    priorities = rank_skills(list(gap_subgraph.nodes), domain, jd_data, mastery_scores, gap_subgraph)
    learning_subgraph = build_learning_subgraph(gap_subgraph, mastery_scores)
    path = generate_learning_path(learning_subgraph, priorities, mastery_scores)
    course_map = {skill: recommend_course(skill, gap_skills, domain) for skill in path}
    reasoning = [
        generate_trace(skill, index, gap_subgraph, priorities, mastery_scores, jd_data)
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
        path=path,
        reasoning=reasoning,
        course_map=course_map,
        mastery_scores=mastery_scores,
        gap_count=len(gap_skills),
        gap_skills=sorted(gap_skills),
        domain=domain,
        graph=graph_payload,
        metrics=metrics,
        pillars=cluster_skills_into_pillars(list(gap_skills))
    )


def analyze_documents(domain: Domain | None, resume: ParsedDocument, jd: ParsedDocument) -> AnalyzeResponse:
    if domain is None:
        domain = get_mapped_domain(jd.text)
    parsed = run_parse(domain, resume, jd)
    pathway = run_pathway(domain, parsed.resume_skills, parsed.jd_data, parsed.mastery_scores)
    warnings = [
        *parsed.parse_metadata["resume"].warnings,
        *parsed.parse_metadata["jd"].warnings,
    ]
    headline = "Path is ready for onboarding"
    if pathway.gap_count >= 8:
        headline = "Large role gap with clear dependency path"
    elif pathway.gap_count >= 4:
        headline = "Moderate skill gap with focused ramp plan"
    return AnalyzeResponse(
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
        graph=pathway.graph,
        metrics=pathway.metrics,
        parse_metadata=parsed.parse_metadata or {},
        summary=AnalyzeSummary(
            headline=headline,
            explanation=(
                f"SkillGraph found {pathway.gap_count} gaps in the {(domain or 'Universal').upper()} domain "
                f"and generated a deterministic, dependency-aware path of {len(pathway.path)} steps."
            ),
        ),
        pillars=pathway.pillars,
        warnings=list(dict.fromkeys(warnings)),
    )

