from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Domain = Literal["swe", "data"]
NodeStatus = Literal["mastered", "partial", "critical_gap", "selected_path", "unseen"]


class TextPayload(BaseModel):
    domain: Domain
    resume_text: str = Field(default="")
    jd_text: str = Field(default="")


class ParseMetadata(BaseModel):
    source: str
    filename: str | None = None
    characters: int
    warnings: list[str] = Field(default_factory=list)
    extraction_method: str = "text"
    sections_detected: list[str] = Field(default_factory=list)
    section_character_counts: dict[str, int] = Field(default_factory=dict)


class ResumeSkill(BaseModel):
    skill: str
    mentions: int
    in_recent_experience: bool
    source_sections: list[str] = Field(default_factory=list)
    evidence_score: float = 0.0
    evidence_snippets: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class JDData(BaseModel):
    required: list[str]
    preferred: list[str]
    required_evidence: dict[str, list[str]] = Field(default_factory=dict)
    preferred_evidence: dict[str, list[str]] = Field(default_factory=dict)
    required_evidence_refs: dict[str, list[str]] = Field(default_factory=dict)
    preferred_evidence_refs: dict[str, list[str]] = Field(default_factory=dict)


class ParseResponse(BaseModel):
    api_version: str = "v1"
    domain: Domain
    resume_skills: list[ResumeSkill]
    jd_data: JDData
    mastery_scores: dict[str, float]
    parse_metadata: dict[str, ParseMetadata] | None = None


class PathwayRequest(BaseModel):
    domain: Domain
    resume_skills: list[ResumeSkill]
    jd_data: JDData
    mastery_scores: dict[str, float]


class RecomputeRequest(PathwayRequest):
    learned_skill: str


class Course(BaseModel):
    id: str
    name: str
    covers: list[str]
    difficulty: int
    domain: str
    url: str


class TraceItem(BaseModel):
    skill: str
    position: int
    mastery: float
    required_level: float = 0.0
    gap: float = 0.0
    priority_score: float
    required_by_jd: bool
    preferred_by_jd: bool
    reason_codes: list[str] = Field(default_factory=list)
    unlocks: list[str]
    downstream_depth: int
    reason: str
    evidence: dict[str, str | int | list[str]] = Field(default_factory=dict)


class GraphNode(BaseModel):
    id: str
    label: str
    mastery: float
    status: NodeStatus


class GraphEdge(BaseModel):
    source: str
    target: str


class Metrics(BaseModel):
    redundant_modules_eliminated: int
    naive_path_length: int
    recommended_path_length: int
    reasoning_trace_coverage: int


class GapReport(BaseModel):
    missing: list[str] = Field(default_factory=list)
    weak: list[str] = Field(default_factory=list)
    met: list[str] = Field(default_factory=list)


class PathwayResponse(BaseModel):
    api_version: str = "v1"
    path: list[str]
    reasoning: list[TraceItem]
    course_map: dict[str, Course]
    mastery_scores: dict[str, float]
    gap_count: int
    gap_skills: list[str]
    gap_report: GapReport
    domain: Domain
    graph: dict[str, list[GraphNode] | list[GraphEdge]]
    metrics: Metrics


class AnalyzeSummary(BaseModel):
    headline: str
    explanation: str


class AnalyzeResponse(BaseModel):
    api_version: str = "v1"
    domain: Domain
    all_skills: list[str]
    resume_skills: list[ResumeSkill]
    jd_data: JDData
    mastery_scores: dict[str, float]
    path: list[str]
    reasoning: list[TraceItem]
    course_map: dict[str, Course]
    gap_count: int
    gap_skills: list[str]
    gap_report: GapReport
    graph: dict[str, list[GraphNode] | list[GraphEdge]]
    metrics: Metrics
    parse_metadata: dict[str, ParseMetadata]
    summary: AnalyzeSummary
    warnings: list[str] = Field(default_factory=list)


class SampleScenario(BaseModel):
    id: str
    label: str
    domain: Domain
    story: str


class SampleScenarioDetail(SampleScenario):
    resume_text: str
    jd_text: str
    expected_path_start: list[str]
