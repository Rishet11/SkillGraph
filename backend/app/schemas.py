from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Importance = Literal["required", "preferred", "bonus"]
GapType = Literal["missing", "weak", "adjacent"]
NodeType = Literal[
    "current_skill",
    "target_skill",
    "gap_skill",
    "prerequisite",
    "recommended_course",
]


class TextPayload(BaseModel):
    resume_text: str = Field(default="")
    job_description_text: str = Field(default="")


class ParseMetadata(BaseModel):
    source: str
    filename: str | None = None
    characters: int
    warnings: list[str] = Field(default_factory=list)


class SkillEvidence(BaseModel):
    skill_id: str
    label: str
    mastery_score: int
    evidence_snippets: list[str]
    source_section: str


class TargetSkill(BaseModel):
    skill_id: str
    label: str
    importance: Importance


class MatchResult(BaseModel):
    skill_id: str
    label: str
    status: Literal["matched", "partial"]
    mastery_score: int
    reason: str


class GapResult(BaseModel):
    skill_id: str
    label: str
    gap_type: GapType
    missing_prerequisites: list[str]
    reason: str


class RecommendedCourse(BaseModel):
    course_id: str
    title: str
    provider: str
    url: str
    duration: str


class LearningStep(BaseModel):
    order: int
    skill_id: str
    goal: str
    recommended_courses: list[RecommendedCourse]
    why_now: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: NodeType
    score: int | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    kind: str
    reason: str


class AnalyzeSummary(BaseModel):
    headline: str
    explanation: str


class AnalyzeResponse(BaseModel):
    fit_score: int
    confidence: int
    resume_skills: list[SkillEvidence]
    target_skills: list[TargetSkill]
    matched_skills: list[MatchResult]
    missing_skills: list[GapResult]
    graph: dict[str, list[GraphNode] | list[GraphEdge]]
    learning_path: list[LearningStep]
    summary: AnalyzeSummary
    warnings: list[str]
    parse_metadata: dict[str, ParseMetadata]


class SampleItem(BaseModel):
    id: str
    label: str
    type: Literal["resume", "job_description"]


class SampleContent(BaseModel):
    id: str
    label: str
    type: Literal["resume", "job_description"]
    content: str

