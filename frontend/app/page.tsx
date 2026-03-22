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
    window.scrollTo({ top: 500, behavior: 'smooth' });
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
        {/* Massive Typography Hero without boxes */}
        <section className="hero animate-fade-in stagger-1">
          <span className="section-kicker" style={{ fontSize: '0.85rem' }}>Next-Gen Career Intelligence</span>
          <h1>SkillGraph</h1>
          <p className="hero-copy">
            Bridging the gap between your current expertise and your next big role with explainable, deterministic learning pathways.
          </p>
        </section>

        {/* Input & Workspace Section (Pristine Panels) */}
        <section className="grid animate-fade-in stagger-2" style={{ gridTemplateColumns: '1fr', maxWidth: '1000px', margin: '0 auto' }}>
          
          <div className="panel" style={{ padding: '48px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
              <div>
                <h2>Workspace</h2>
                <p className="muted" style={{ marginTop: 8 }}>Setup your target domain and upload your dossier.</p>
              </div>
              <div style={{ width: '240px' }}>
                <label>Target Domain</label>
                <select
                  className="file-input"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value as Domain)}
                  style={{ cursor: 'pointer' }}
                >
                  <option value="swe">Software Engineering</option>
                  <option value="data">Data Science & AI</option>
                </select>
              </div>
            </div>

            <div className="grid" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '32px' }}>
              <div>
                <span className="section-kicker">Input 01</span>
                <label style={{ fontSize: '1.1rem', marginBottom: 16 }}>Personal Dossier</label>
                <textarea
                  className="textarea"
                  placeholder="Paste resume transcript..."
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  style={{ minHeight: '160px', marginBottom: 16 }}
                />
                <div style={{ border: '1px dashed var(--border-strong)', padding: '16px', borderRadius: '12px', textAlign: 'center', background: 'var(--bg)' }}>
                  <label style={{ cursor: 'pointer', margin: 0, color: 'var(--primary)' }}>
                    {resumeFile ? 'File Selected' : '📁 Upload PDF / DOC'}
                    <input
                      type="file"
                      onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                      accept=".pdf,.doc,.docx"
                      style={{ display: 'none' }}
                    />
                  </label>
                  {resumeFile && <div className="pill good" style={{ marginTop: 12 }}>{resumeFile.name}</div>}
                </div>
              </div>

              <div>
                <span className="section-kicker">Input 02</span>
                <label style={{ fontSize: '1.1rem', marginBottom: 16 }}>Target Specification</label>
                <textarea
                  className="textarea"
                  placeholder="Paste job description..."
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  style={{ minHeight: '160px', marginBottom: 16 }}
                />
                <div style={{ border: '1px dashed var(--border-strong)', padding: '16px', borderRadius: '12px', textAlign: 'center', background: 'var(--bg)' }}>
                  <label style={{ cursor: 'pointer', margin: 0, color: 'var(--primary)' }}>
                    {jdFile ? 'File Selected' : '📁 Upload PDF / DOC'}
                    <input
                      type="file"
                      onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                      accept=".pdf,.doc,.docx"
                      style={{ display: 'none' }}
                    />
                  </label>
                  {jdFile && <div className="pill good" style={{ marginTop: 12 }}>{jdFile.name}</div>}
                </div>
              </div>
            </div>

            <div style={{ marginTop: 40, paddingTop: 32, borderTop: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', gap: '16px' }}>
                <button className="button button-primary" disabled={isPending} onClick={runAnalysis} style={{ flex: 2, padding: '20px', fontSize: '1.1rem' }}>
                  {isPending ? "Generating Insight..." : "Run SkillGraph Engine →"}
                </button>
                <button
                  className="button button-secondary"
                  onClick={() => {
                    setResult(null); setError(null); setResumeText(""); setJdText("");
                    setResumeFile(null); setJdFile(null);
                  }}
                  style={{ flex: 1 }}
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          <div style={{ marginTop: 24, textAlign: 'center' }}>
            <span className="section-kicker">Quick Start</span>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap', marginTop: 16 }}>
              {samples.map((sample) => (
                <button
                  className="button button-secondary"
                  key={sample.id}
                  onClick={() => loadSampleScenario(sample.id)}
                  style={{ fontSize: '0.85rem' }}
                >
                  {sample.label}
                </button>
              ))}
            </div>
            {sampleStory && <p className="muted" style={{ marginTop: 16, fontSize: '0.9rem' }}>{sampleStory}</p>}
          </div>

        </section>

        {isPending && (
          <section className="panel animate-fade-in" style={{ marginTop: 60, textAlign: 'center', borderColor: 'var(--primary)', maxWidth: '1000px', margin: '60px auto 0' }}>
            <span className="section-kicker">Processing via Hybrid AI Pipeline</span>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: 24, flexWrap: 'wrap' }}>
              {loadingSteps.map((step, i) => (
                <span className="pill primary" key={step} style={{ animationDelay: `${i * 0.15}s` }}>
                  {i+1}. {step}
                </span>
              ))}
            </div>
          </section>
        )}

        {error && (
          <section className="panel" style={{ marginTop: 60, borderColor: 'var(--warning)', maxWidth: '1000px', margin: '60px auto 0' }}>
            <h3 style={{ color: 'var(--warning)' }}>Engine Fallback</h3>
            <p className="muted" style={{ marginTop: 8 }}>{error}</p>
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
