"use client";

import { useEffect, useState, useTransition } from "react";

import { ResultDashboard } from "../components/ResultDashboard";
import { analyzeFiles, fetchSampleContent, fetchSamples, recomputePath } from "../lib/api";
import { AnalyzeResponse, Domain, SampleScenario } from "../lib/types";

const loadingSteps = ["Parsing", "Scoring mastery", "Building gap graph", "Prioritizing path", "Writing trace"];

export default function HomePage() {
  const [domain, setDomain] = useState<Domain>("data");
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [samples, setSamples] = useState<SampleScenario[]>([]);
  const [sampleStory, setSampleStory] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [isRecomputing, startRecompute] = useTransition();

  useEffect(() => {
    fetchSamples().then(setSamples).catch(() => undefined);
  }, []);

  const runAnalysis = () => {
    setError(null);
    startTransition(async () => {
      try {
        const response = await analyzeFiles({
          domain,
          resume_file: resumeFile,
          jd_file: jdFile,
          resume_text: resumeText,
          jd_text: jdText
        });
        setResult(response);
      } catch (analysisError) {
        setResult(null);
        setError(analysisError instanceof Error ? analysisError.message : "Analysis failed.");
      }
    });
  };

  const loadSampleScenario = async (sampleId: string) => {
    const scenario = await fetchSampleContent(sampleId);
    setDomain(scenario.domain);
    setResumeText(scenario.resume_text);
    setJdText(scenario.jd_text);
    setResumeFile(null);
    setJdFile(null);
    setSampleStory(scenario.story);
  };

  const markLearned = (skill: string) => {
    if (!result) {
      return;
    }
    startRecompute(async () => {
      try {
        const updated = await recomputePath({
          domain: result.domain,
          resume_skills: result.resume_skills,
          jd_data: result.jd_data,
          mastery_scores: result.mastery_scores,
          learned_skill: skill
        });
        setResult({
          ...result,
          api_version: updated.api_version,
          mastery_scores: updated.mastery_scores,
          path: updated.path,
          reasoning: updated.reasoning,
          course_map: updated.course_map,
          gap_count: updated.gap_count,
          gap_skills: updated.gap_skills,
          gap_report: updated.gap_report,
          graph: updated.graph,
          metrics: updated.metrics,
          summary: {
            headline: "Path recomputed after learning update",
            explanation: `Marked ${skill} as learned and regenerated the dependency-aware path.`
          }
        });
      } catch (recomputeError) {
        setError(recomputeError instanceof Error ? recomputeError.message : "Recompute failed.");
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
              <h1>Explainable adaptive onboarding</h1>
              <p className="hero-copy">
                Parse a resume and job description, classify skills into a fixed taxonomy, compute mastery, identify the gap subgraph, and generate a deterministic learning path with a visible reasoning trace.
              </p>
            </div>
            <div className="hero-stats">
              <div className="stat-card">
                <span className="muted">Domains</span>
                <strong>SWE + Data</strong>
              </div>
              <div className="stat-card">
                <span className="muted">Adaptive proof</span>
                <strong>Mark learned</strong>
              </div>
              <div className="stat-card">
                <span className="muted">Grounding</span>
                <strong>Fixed catalog</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="main-grid grid">
          <div className="panel">
            <p className="section-kicker">Input</p>
            <h2>Build the pathway</h2>
            <div className="field">
              <label htmlFor="domain">Domain</label>
              <select
                id="domain"
                className="file-input"
                value={domain}
                onChange={(event) => setDomain(event.target.value as Domain)}
              >
                <option value="data">Data</option>
                <option value="swe">SWE</option>
              </select>
            </div>
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
                  placeholder="Or paste resume text..."
                  value={resumeText}
                  onChange={(event) => setResumeText(event.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="jd-file">Job description upload</label>
                <input
                  id="jd-file"
                  className="file-input"
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(event) => setJdFile(event.target.files?.[0] ?? null)}
                />
                <textarea
                  className="textarea"
                  placeholder="Or paste job description text..."
                  value={jdText}
                  onChange={(event) => setJdText(event.target.value)}
                />
              </div>
            </div>
            <div className="actions" style={{ marginTop: 18 }}>
              <button className="button button-primary" disabled={isPending} onClick={runAnalysis}>
                {isPending ? "Building path..." : "Run SkillGraph"}
              </button>
              <button
                className="button button-secondary"
                onClick={() => {
                  setResult(null);
                  setError(null);
                  setSampleStory(null);
                  setResumeFile(null);
                  setJdFile(null);
                  setResumeText("");
                  setJdText("");
                }}
              >
                Reset
              </button>
            </div>
          </div>

          <div className="panel">
            <p className="section-kicker">Fixed Demo Inputs</p>
            <h2>Use the tested scenarios</h2>
            <div className="grid">
              {samples.map((sample) => (
                <button
                  className="sample-button"
                  key={sample.id}
                  onClick={() => loadSampleScenario(sample.id)}
                >
                  <strong>{sample.label}</strong>
                  <p className="muted">{sample.domain.toUpperCase()} domain</p>
                  <p className="muted">{sample.story}</p>
                </button>
              ))}
            </div>
            {sampleStory && (
              <div className="callout" style={{ marginTop: 18 }}>
                <strong>Demo story</strong>
                <p className="muted">{sampleStory}</p>
              </div>
            )}
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
              <span className="pill warn">Try the fixed demo scenarios</span>
              <span className="pill">Paste text directly</span>
            </div>
          </section>
        )}

        {result && (
          <ResultDashboard
            result={result}
            onMarkLearned={markLearned}
            isRecomputing={isRecomputing}
          />
        )}
      </div>
    </main>
  );
}
