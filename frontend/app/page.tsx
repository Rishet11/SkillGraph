"use client";

import { useEffect, useState, useTransition } from "react";

import { ResultDashboard } from "../components/ResultDashboard";
import { analyzeFiles, fetchSampleContent, fetchSamples, recomputePath } from "../lib/api";
import { AnalyzeResponse, Domain, SampleScenario } from "../lib/types";

const loadingSteps = ["Parsing Deeply", "Scoring mastery", "Mapping gap graph", "Prioritizing path", "Writing trace"];

export default function HomePage() {
  const [domain, setDomain] = useState<Domain>("swe");
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
    // Auto-scroll to inputs
    window.scrollTo({ top: 600, behavior: 'smooth' });
  };

  const markLearned = (skill: string) => {
    if (!result) return;
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
          mastery_scores: updated.mastery_scores,
          path: updated.path,
          reasoning: updated.reasoning,
          course_map: updated.course_map,
          gap_count: updated.gap_count,
          gap_skills: updated.gap_skills,
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
        {/* Cinematic Hero */}
        <section className="hero animate-fade-in stagger-1">
          <div style={{ textAlign: 'center', maxWidth: '800px', margin: '0 auto' }}>
            <p className="section-kicker">Next-Gen Career Intelligence</p>
            <h1>SkillGraph <span style={{ color: 'var(--secondary)' }}>v2</span></h1>
            <p className="hero-copy" style={{ margin: '0 auto 40px' }}>
              Bridging the gap between your current expertise and your next big role with explainable, deterministic learning pathways.
            </p>
            
            <div className="hero-stats" style={{ justifyContent: 'center' }}>
              <div className="stat-card">
                <span className="muted">Processing Engine</span>
                <strong>Gemini + BERT</strong>
              </div>
              <div className="stat-card">
                <span className="muted">Visualization</span>
                <strong>React Flow</strong>
              </div>
              <div className="stat-card">
                <span className="muted">Stability</span>
                <strong>Python 3.13</strong>
              </div>
            </div>
          </div>
        </section>

        {/* Input & Scenarios Section */}
        <section className="main-grid grid animate-fade-in stagger-2">
          <div className="panel">
            <p className="section-kicker">Workspace</p>
            <h2>Analysis Engine</h2>
            
            <div className="grid" style={{ marginTop: 20 }}>
              <div className="field">
                <label>Target career domain</label>
                <select
                  className="file-input"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value as Domain)}
                >
                  <option value="swe">Software Engineering</option>
                  <option value="data">Data Science & AI</option>
                </select>
              </div>

              <div className="upload-grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '24px', marginTop: 24 }}>
                <div className="field">
                  <label className="section-kicker" style={{ fontSize: '0.65rem' }}>Personal Dossier</label>
                  <div className="grid" style={{ gap: '12px' }}>
                    <textarea
                      className="textarea"
                      placeholder="Paste resume transcript..."
                      value={resumeText}
                      onChange={(e) => setResumeText(e.target.value)}
                      style={{ minHeight: '140px' }}
                    />
                    <div className="panel" style={{ padding: '16px', background: 'rgba(255,255,255,0.3)', border: '1px dashed var(--line)' }}>
                      <label className="mono" style={{ fontSize: '0.65rem', display: 'block', marginBottom: 8 }}>OR UPLOAD PDF/DOC</label>
                      <input
                        type="file"
                        className="file-input"
                        onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                        accept=".pdf,.doc,.docx"
                        style={{ fontSize: '0.75rem' }}
                      />
                      {resumeFile && <div className="pill good" style={{ marginTop: 8, fontSize: '0.7rem' }}>{resumeFile.name} Loaded</div>}
                    </div>
                  </div>
                </div>

                <div className="field">
                  <label className="section-kicker" style={{ fontSize: '0.65rem' }}>Target Specification</label>
                  <div className="grid" style={{ gap: '12px' }}>
                    <textarea
                      className="textarea"
                      placeholder="Paste job description..."
                      value={jdText}
                      onChange={(e) => setJdText(e.target.value)}
                      style={{ minHeight: '140px' }}
                    />
                    <div className="panel" style={{ padding: '16px', background: 'rgba(255,255,255,0.3)', border: '1px dashed var(--line)' }}>
                      <label className="mono" style={{ fontSize: '0.65rem', display: 'block', marginBottom: 8 }}>OR UPLOAD PDF/DOC</label>
                      <input
                        type="file"
                        className="file-input"
                        onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                        accept=".pdf,.doc,.docx"
                        style={{ fontSize: '0.75rem' }}
                      />
                      {jdFile && <div className="pill good" style={{ marginTop: 8, fontSize: '0.7rem' }}>{jdFile.name} Loaded</div>}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="actions" style={{ marginTop: 32, paddingTop: 24, borderTop: '1px solid var(--line)' }}>
              <button className="button button-primary" disabled={isPending} onClick={runAnalysis} style={{ width: '100%', fontSize: '1.2rem', padding: '20px' }}>
                {isPending ? "Generating Insight..." : "Run SkillGraph Engine →"}
              </button>
              <button
                className="button button-secondary"
                onClick={() => {
                  setResult(null); setError(null); setResumeText(""); setJdText("");
                  setResumeFile(null); setJdFile(null);
                }}
                style={{ width: '100%', marginTop: 12 }}
              >
                Reset Workspace
              </button>
            </div>
          </div>

          <div className="panel">
            <p className="section-kicker">Library</p>
            <h2>Verified Scenarios</h2>
            <div className="grid">
              {samples.map((sample) => (
                <button
                  className="sample-button"
                  key={sample.id}
                  onClick={() => loadSampleScenario(sample.id)}
                  style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--panel-border)' }}
                >
                  <div style={{ color: 'var(--secondary)', fontWeight: 700, marginBottom: 4 }}>{sample.label}</div>
                  <p className="muted" style={{ fontSize: '0.85rem' }}>{sample.story}</p>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Luminous Loading State */}
        {isPending && (
          <section className="panel animate-fade-in" style={{ marginTop: 26, textAlign: 'center', border: '1px solid var(--primary)' }}>
            <p className="section-kicker">Engine is running...</p>
            <div className="loading-steps" style={{ justifyContent: 'center', marginTop: 16 }}>
              {loadingSteps.map((step, i) => (
                <span className="loading-step" key={step} style={{ animationDelay: `${i * 0.2}s`, background: 'var(--primary-glow)', border: '1px solid var(--primary)' }}>
                  {step}
                </span>
              ))}
            </div>
          </section>
        )}

        {error && (
          <section className="panel" style={{ marginTop: 26, border: '1px solid var(--error)' }}>
            <h3>Engine Fallback</h3>
            <p className="muted">{error}</p>
          </section>
        )}

        {/* Dashboard Placeholder/Result */}
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
