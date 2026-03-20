import { AnalyzeResponse, SampleItem } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchSamples(): Promise<SampleItem[]> {
  const response = await fetch(`${API_BASE}/samples`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load samples.");
  }
  return response.json();
}

export async function fetchSampleContent(id: string): Promise<string> {
  const response = await fetch(`${API_BASE}/samples/${id}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load sample content.");
  }
  const body = await response.json();
  return body.content;
}

export async function analyzeText(input: {
  resume_text: string;
  job_description_text: string;
}): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(input)
  });
  if (!response.ok) {
    const detail = await safeDetail(response);
    throw new Error(detail);
  }
  return response.json();
}

export async function analyzeFiles(input: {
  resume_file?: File | null;
  job_description_file?: File | null;
  resume_text: string;
  job_description_text: string;
}): Promise<AnalyzeResponse> {
  const useFiles = input.resume_file || input.job_description_file;
  if (!useFiles) {
    return analyzeText({
      resume_text: input.resume_text,
      job_description_text: input.job_description_text
    });
  }
  const formData = new FormData();
  if (input.resume_file) {
    formData.append("resume_file", input.resume_file);
  }
  if (input.job_description_file) {
    formData.append("job_description_file", input.job_description_file);
  }
  formData.append("resume_text", input.resume_text);
  formData.append("job_description_text", input.job_description_text);
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    body: formData
  });
  if (!response.ok) {
    const detail = await safeDetail(response);
    throw new Error(detail);
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
