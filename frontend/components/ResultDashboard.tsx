"use client";

import { AnalyzeResponse } from "../lib/types";
import { GraphPanel } from "./GraphPanel";
import { PillarDashboard } from "./PillarDashboard";

type Props = {
  result: AnalyzeResponse;
  onMarkLearned: (skill: string) => void;
  isRecomputing: boolean;
};

export function ResultDashboard({ result, onMarkLearned, isRecomputing }: Props) {
  return (
    <section className="animate-fade-in stagger-1" style={{ marginTop: 80, borderTop: '1px solid var(--border)', paddingTop: 80 }}>
      {/* Top Section: Outcome Summary & Metrics */}
      <div style={{ marginBottom: 48 }}>
        <div className="grid" style={{ gridTemplateColumns: 'minmax(0, 1.5fr) minmax(0, 1fr)', gap: '60px', alignItems: 'center' }}>
          <div>
            <span className="section-kicker">Analysis Outcome</span>
            <h2 style={{ fontSize: "3.5rem", lineHeight: 1.1, marginBottom: 20 }}>{result.summary.headline}</h2>
            <p className="muted" style={{ fontSize: "1.25rem", maxWidth: '700px' }}>{result.summary.explanation}</p>
          </div>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <div className="panel" style={{ padding: '32px', textAlign: 'center' }}>
              <span className="section-kicker">Skill Gaps</span>
              <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--warning)' }}>{result.gap_count}</div>
            </div>
            <div className="panel" style={{ padding: '32px', textAlign: 'center' }}>
              <span className="section-kicker">Path Steps</span>
              <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--primary)' }}>{result.path.length}</div>
            </div>
            <div className="panel" style={{ padding: '32px', textAlign: 'center', gridColumn: 'span 2' }}>
              <span className="section-kicker">Efficiency Gain</span>
              <div style={{ fontSize: '3rem', fontWeight: 800, color: 'var(--success)' }}>{result.metrics.redundant_modules_eliminated}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Section: Full-Width Directed Graph */}
      <div className="panel" style={{ marginBottom: 48, padding: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: 24 }}>
          <div>
            <h2>Dependency Trace Map</h2>
            <p className="muted" style={{ marginTop: 8 }}>A deterministic map of prerequisite hierarchies.</p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
             <span className="pill good">Mastered</span>
             <span className="pill warn">Gap Detected</span>
             <span className="pill primary">Optimal Path</span>
          </div>
        </div>
        <div style={{ border: '1px solid var(--border)', borderRadius: '16px', overflow: 'hidden', height: '700px', background: 'var(--bg)' }}>
          <GraphPanel graph={result.graph} />
        </div>
      </div>

      {/* Middle Section: Clustered Pillars */}
      <div style={{ marginBottom: 48 }}>
        <PillarDashboard pillars={result.pillars} />
      </div>

      {/* Bottom Section: 2-Column Details (Ledger & Roadmap) */}
      <div className="grid" style={{ gridTemplateColumns: '1fr 1.5fr', gap: '40px', alignItems: 'start' }}>
        {/* Left: Skill Ledger */}
        <div className="panel" style={{ alignSelf: 'stretch', padding: '40px' }}>
          <span className="section-kicker">Validation Ledger</span>
          <h3 style={{ marginBottom: 32 }}>Full Skill Inventory</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {result.all_skills.map((skill) => {
              const mastery = result.mastery_scores[skill] ?? 0;
              const isGap = result.gap_skills.includes(skill);
              return (
                <div className="list-item" key={skill} style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: '1rem' }}>{skill}</span>
                    <span className={`pill ${mastery >= 0.8 ? "good" : isGap ? "warn" : ""}`}>
                      {(mastery * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="mastery-track">
                    <div className="mastery-fill" style={{ width: `${mastery * 100}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Adaptive Roadmap */}
        <div className="panel" style={{ alignSelf: 'stretch', padding: '40px' }}>
          <span className="section-kicker">Learning Trajectory</span>
          <h3 style={{ marginBottom: 40 }}>Adaptive Step-by-Step Pathway</h3>
          <div>
            {result.reasoning.map((trace, idx) => {
              const course = result.course_map[trace.skill];
              return (
                <div 
                  className="roadmap-step animate-fade-in" 
                  key={trace.skill}
                  style={{ animationDelay: `${0.1 * idx}s`, paddingBottom: 56 }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 20 }}>
                    <div>
                      <div className="section-kicker">Phase {trace.position}</div>
                      <div style={{ fontWeight: 800, fontSize: '1.5rem', color: 'var(--primary)' }}>{trace.skill}</div>
                    </div>
                    <button
                      className="button button-secondary"
                      disabled={isRecomputing}
                      onClick={() => onMarkLearned(trace.skill)}
                      style={{ padding: '10px 20px', fontSize: '0.85rem' }}
                    >
                      {isRecomputing ? "Tracing..." : "Complete Milestone"}
                    </button>
                  </div>
                  <p className="muted" style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: 24 }}>{trace.reason}</p>
                  
                  {course && (
                    <div className="course-card">
                      <div className="section-kicker" style={{ color: 'var(--ink)' }}>Recommended Resource</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, margin: '8px 0' }}>{course.name}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12 }}>
                         <span className="pill">Level: {course.difficulty}/10</span>
                         <span className="muted" style={{ fontSize: '0.85rem' }}>Source: {course.url.split('/')[2]}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
