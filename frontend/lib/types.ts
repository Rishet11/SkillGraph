export type AnalyzeResponse = {
  fit_score: number;
  confidence: number;
  resume_skills: SkillEvidence[];
  target_skills: TargetSkill[];
  matched_skills: MatchResult[];
  missing_skills: GapResult[];
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
  learning_path: LearningStep[];
  summary: {
    headline: string;
    explanation: string;
  };
  warnings: string[];
  parse_metadata: Record<string, ParseMetadata>;
};

export type ParseMetadata = {
  source: string;
  filename?: string | null;
  characters: number;
  warnings: string[];
};

export type SkillEvidence = {
  skill_id: string;
  label: string;
  mastery_score: number;
  evidence_snippets: string[];
  source_section: string;
};

export type TargetSkill = {
  skill_id: string;
  label: string;
  importance: "required" | "preferred" | "bonus";
};

export type MatchResult = {
  skill_id: string;
  label: string;
  status: "matched" | "partial";
  mastery_score: number;
  reason: string;
};

export type GapResult = {
  skill_id: string;
  label: string;
  gap_type: "missing" | "weak" | "adjacent";
  missing_prerequisites: string[];
  reason: string;
};

export type GraphNode = {
  id: string;
  label: string;
  type:
    | "current_skill"
    | "target_skill"
    | "gap_skill"
    | "prerequisite"
    | "recommended_course";
  score?: number | null;
};

export type GraphEdge = {
  source: string;
  target: string;
  kind: string;
  reason: string;
};

export type RecommendedCourse = {
  course_id: string;
  title: string;
  provider: string;
  url: string;
  duration: string;
};

export type LearningStep = {
  order: number;
  skill_id: string;
  goal: string;
  recommended_courses: RecommendedCourse[];
  why_now: string;
};

export type SampleItem = {
  id: string;
  label: string;
  type: "resume" | "job_description";
};

