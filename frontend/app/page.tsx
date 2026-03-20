"use client";

import { useEffect, useState, useTransition } from "react";

import { ResultDashboard } from "../components/ResultDashboard";
import { analyzeFiles, fetchSampleContent, fetchSamples } from "../lib/api";
import { AnalyzeResponse, SampleItem } from "../lib/types";

const loadingSteps = ["Parsing", "Extracting", "Scoring", "Graphing", "Recommending"];

export default function HomePage() {
  const [resumeText, setResumeText] = useState("");
  const [jobText, setJobText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobFile, setJobFile] = useState<File | null>(null);
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    fetchSamples().then(setSamples).catch(() => undefined);
  }, []);

  const sampleResumes = samples.filter((sample) => sample.type === "resume");
  const sampleRoles = samples.filter((sample) => sample.type === "job_description");

  const loadSample = async (sampleId: string, target: "resume" | "job") => {
    const content = await fetchSampleContent(sampleId);
    if (target === "resume") {
      setResumeText(content);
      setResumeFile(null);
      return;
    }
    setJobText(content);
    setJobFile(null);
  };

  const runAnalysis = () => {
    setError(null);
    startTransition(async () => {
      try {
        const response = await analyzeFiles({
          resume_file: resumeFile,
          job_description_file: jobFile,
          resume_text: resumeText,
          job_description_text: jobText
        });
        setResult(response);
      } catch (analysisError) {
        setResult(null);
        setError(
          analysisError instanceof Error ? analysisError.message : "SkillGraph analysis failed."
        );
      }
    });
  };

  return (
    <main className="page-shell">
      <div className="container">
        <section className="hero">
          <div className="hero-grid">
            <div>
              <p className="hero-kicker">SkillGraph</p>
              <h1>AI-Adaptive Onboarding Engine</h1>
              <p className="hero-copy">
                Upload a resume and a target role. SkillGraph extracts evidence, scores readiness,
                maps missing prerequisites, and turns the gap into an explainable learning path.
              </p>
            </div>
            <div className="hero-stats">
              <div className="stat-card">
                <span className="muted">Core mode</span>
                <strong>Deterministic</strong>
              </div>
              <div className="stat-card">
                <span className="muted">Demo paths</span>
                <strong>Upload + samples</strong>
              </div>
              <div className="stat-card">
                <span className="muted">Audience</span>
                <strong>Hackathon judges</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="main-grid grid">
          <div className="panel">
            <p className="section-kicker">Input</p>
            <h2>Analyze candidate fit</h2>
            <p className="muted">
              Use real uploads when available. Keep sample scenarios ready for a stable stage demo.
            </p>

            <div className="upload-grid">
              <div className="field">
                <label htmlFor="resume-file">Resume upload</label>
                <input
                  id="resume-file"
                  className="file-input"
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
                />
                <textarea
                  className="textarea"
                  placeholder="Or paste resume text here..."
                  value={resumeText}
                  onChange={(event) => setResumeText(event.target.value)}
                />
              </div>

              <div className="field">
                <label htmlFor="job-file">Job description upload</label>
                <input
                  id="job-file"
                  className="file-input"
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(event) => setJobFile(event.target.files?.[0] ?? null)}
                />
                <textarea
                  className="textarea"
                  placeholder="Or paste job description here..."
                  value={jobText}
                  onChange={(event) => setJobText(event.target.value)}
                />
              </div>
            </div>

            <div className="actions" style={{ marginTop: 18 }}>
              <button className="button button-primary" disabled={isPending} onClick={runAnalysis}>
                {isPending ? "Analyzing..." : "Run SkillGraph"}
              </button>
              <button
                className="button button-secondary"
                onClick={() => {
                  setResumeText("");
                  setJobText("");
                  setResumeFile(null);
                  setJobFile(null);
                  setResult(null);
                  setError(null);
                }}
              >
                Reset demo
              </button>
            </div>
          </div>

          <div className="panel">
            <p className="section-kicker">Fallback Samples</p>
            <h2>Demo-safe candidate and role packs</h2>
            <div className="sample-grid">
              <div className="grid">
                {sampleResumes.map((sample) => (
                  <button
                    className="sample-button"
                    key={sample.id}
                    onClick={() => loadSample(sample.id, "resume")}
                  >
                    <strong>{sample.label}</strong>
                    <p className="muted">Load as candidate profile</p>
                  </button>
                ))}
              </div>
              <div className="grid">
                {sampleRoles.map((sample) => (
                  <button
                    className="sample-button"
                    key={sample.id}
                    onClick={() => loadSample(sample.id, "job")}
                  >
                    <strong>{sample.label}</strong>
                    <p className="muted">Load as target role</p>
                  </button>
                ))}
              </div>
            </div>

            <div style={{ marginTop: 18 }}>
              <h3>How it works</h3>
              <p className="muted">
                The backend extracts canonical skills, computes mastery from evidence density,
                identifies missing prerequisites, and returns a reproducible learning roadmap.
              </p>
            </div>
          </div>
        </section>

        {isPending && (
          <section className="panel" style={{ marginTop: 26 }}>
            <p className="section-kicker">Live Progress</p>
            <div className="loading-steps">
              {loadingSteps.map((step) => (
                <span className="loading-step" key={step}>
                  {step}
                </span>
              ))}
            </div>
          </section>
        )}

        {error && (
          <section className="panel" style={{ marginTop: 26 }}>
            <h3>Fallback triggered</h3>
            <p className="muted">{error}</p>
            <div className="badge-row">
              <span className="pill warn">Try sample inputs</span>
              <span className="pill">Paste text directly</span>
            </div>
          </section>
        )}

        {result && <ResultDashboard result={result} />}
      </div>
    </main>
  );
}

