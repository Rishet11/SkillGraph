import {
  AnalyzeResponse,
  Domain,
  JDData,
  PathwayResponse,
  ResumeSkill,
  SampleScenario,
  SampleScenarioDetail
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchSamples(): Promise<SampleScenario[]> {
  const response = await fetch(`${API_BASE}/samples`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load demo scenarios.");
  }
  return response.json();
}

export async function fetchSampleContent(id: string): Promise<SampleScenarioDetail> {
  const response = await fetch(`${API_BASE}/samples/${id}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load sample scenario.");
  }
  return response.json();
}

export async function analyzeFiles(input: {
  domain: Domain;
  resume_file?: File | null;
  jd_file?: File | null;
  resume_text: string;
  jd_text: string;
}): Promise<AnalyzeResponse> {
  const useFiles = input.resume_file || input.jd_file;
  if (!useFiles) {
    return analyzeText(input);
  }
  const formData = new FormData();
  formData.append("domain", input.domain);
  if (input.resume_file) {
    formData.append("resume_file", input.resume_file);
  }
  if (input.jd_file) {
    formData.append("jd_file", input.jd_file);
  }
  formData.append("resume_text", input.resume_text);
  formData.append("jd_text", input.jd_text);
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    throw new Error(await safeDetail(response));
  }
  return response.json();
}

export async function analyzeText(input: {
  domain: Domain;
  resume_text: string;
  jd_text: string;
}): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });
  if (!response.ok) {
    throw new Error(await safeDetail(response));
  }
  return response.json();
}

export async function recomputePath(input: {
  domain: Domain;
  resume_skills: ResumeSkill[];
  jd_data: JDData;
  mastery_scores: Record<string, number>;
  learned_skill: string;
}): Promise<PathwayResponse> {
  const response = await fetch(`${API_BASE}/recompute`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });
  if (!response.ok) {
    throw new Error(await safeDetail(response));
  }
  return response.json();
}

async function safeDetail(response: Response) {
  try {
    const body = await response.json();
    return body.detail ?? "Analysis failed.";
  } catch {
    return "Analysis failed.";
  }
}

