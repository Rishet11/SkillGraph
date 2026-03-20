export type Domain = "swe" | "data";

export type ParseMetadata = {
  source: string;
  filename?: string | null;
  characters: number;
  warnings: string[];
};

export type ResumeSkill = {
  skill: string;
  mentions: number;
  in_recent_experience: boolean;
};

export type JDData = {
  required: string[];
  preferred: string[];
};

export type Course = {
  id: string;
  name: string;
  covers: string[];
  difficulty: number;
  domain: string;
  url: string;
};

export type TraceItem = {
  skill: string;
  position: number;
  mastery: number;
  priority_score: number;
  required_by_jd: boolean;
  preferred_by_jd: boolean;
  unlocks: string[];
  downstream_depth: number;
  reason: string;
};

export type GraphNode = {
  id: string;
  label: string;
  mastery: number;
  status: "mastered" | "partial" | "critical_gap" | "selected_path" | "unseen";
};

export type GraphEdge = {
  source: string;
  target: string;
};

export type Metrics = {
  redundant_modules_eliminated: number;
  naive_path_length: number;
  recommended_path_length: number;
  reasoning_trace_coverage: number;
};

export type AnalyzeResponse = {
  domain: Domain;
  all_skills: string[];
  resume_skills: ResumeSkill[];
  jd_data: JDData;
  mastery_scores: Record<string, number>;
  path: string[];
  reasoning: TraceItem[];
  course_map: Record<string, Course>;
  gap_count: number;
  gap_skills: string[];
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
  metrics: Metrics;
  parse_metadata: Record<string, ParseMetadata>;
  summary: {
    headline: string;
    explanation: string;
  };
  warnings: string[];
};

export type PathwayResponse = {
  path: string[];
  reasoning: TraceItem[];
  course_map: Record<string, Course>;
  mastery_scores: Record<string, number>;
  gap_count: number;
  gap_skills: string[];
  domain: Domain;
  graph: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
  metrics: Metrics;
};

export type SampleScenario = {
  id: string;
  label: string;
  domain: Domain;
  story: string;
};

export type SampleScenarioDetail = SampleScenario & {
  resume_text: string;
  jd_text: string;
  expected_path_start: string[];
};

