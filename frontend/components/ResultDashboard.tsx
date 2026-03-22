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
    <section className="animate-fade-in stagger-1" style={{ marginTop: 60, borderTop: '2px solid var(--line)', paddingTop: 60 }}>
      {/* Top Section: Outcome Summary & Metrics */}
      <div className="panel" style={{ marginBottom: 32, border: 'none', background: 'transparent', boxShadow: 'none', padding: 0 }}>
        <div className="grid" style={{ gridTemplateColumns: 'minmax(0, 1.5fr) minmax(0, 1fr)', gap: '40px', alignItems: 'start' }}>
          <div>
            <span className="section-kicker">Analysis Outcome</span>
            <h2 style={{ fontSize: "3rem", lineHeight: 1.1, marginBottom: 16 }}>{result.summary.headline}</h2>
            <p className="muted" style={{ fontSize: "1.2rem", maxWidth: '700px' }}>{result.summary.explanation}</p>
          </div>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div className="score-card panel" style={{ padding: '24px', textAlign: 'center' }}>
              <span className="section-kicker" style={{ fontSize: '0.6rem' }}>Skill Gaps</span>
              <div className="value" style={{ fontSize: '2.5rem', fontWeight: 800 }}>{result.gap_count}</div>
            </div>
            <div className="score-card panel" style={{ padding: '24px', textAlign: 'center' }}>
              <span className="section-kicker" style={{ fontSize: '0.6rem' }}>Complexity</span>
              <div className="value" style={{ fontSize: '2.5rem', fontWeight: 800 }}>{result.path.length}</div>
            </div>
            <div className="score-card panel" style={{ padding: '24px', textAlign: 'center' }}>
              <span className="section-kicker" style={{ fontSize: '0.6rem' }}>Efficiency</span>
              <div className="value" style={{ fontSize: '2.5rem', fontWeight: 800 }}>{result.metrics.redundant_modules_eliminated}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Section: Full-Width Directed Graph */}
      <div className="panel" style={{ marginBottom: 32, padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: 20 }}>
          <div>
            <span className="section-kicker">Interactive Schematic</span>
            <h3 style={{ fontSize: '1.8rem' }}>Dependency Trace Map</h3>
          </div>
          <div className="muted" style={{ fontSize: '0.85rem', maxWidth: '400px', textAlign: 'right' }}>
            A deterministic map of prerequisite hierarchies. <br/>
            <span style={{ color: 'var(--accent-3)', fontWeight: 700 }}>Green</span>: Mastered | <span style={{ color: 'var(--accent-2)', fontWeight: 700 }}>Orange</span>: Gap | <span style={{ color: 'var(--accent)', fontWeight: 700 }}>Blue</span>: Optimal Path
          </div>
        </div>
        <div style={{ border: '1px solid var(--line)', borderRadius: '16px', overflow: 'hidden', height: '700px', background: 'rgba(255,255,255,0.4)' }}>
          <GraphPanel graph={result.graph} />
        </div>
      </div>

      {/* Middle Section: Clustered Pillars */}
      <div style={{ marginBottom: 40 }}>
        <PillarDashboard pillars={result.pillars} />
      </div>

      {/* Bottom Section: 2-Column Details (Ledger & Roadmap) */}
      <div className="grid" style={{ gridTemplateColumns: '1fr 1.5fr', gap: '32px', alignItems: 'start' }}>
        {/* Left: Skill Ledger */}
        <div className="panel" style={{ alignSelf: 'stretch' }}>
          <span className="section-kicker">Validation Ledger</span>
          <h3 style={{ marginBottom: 24, fontSize: '1.5rem' }}>Full Skill Inventory</h3>
          <div className="grid" style={{ gap: '12px' }}>
            {result.all_skills.map((skill) => {
              const mastery = result.mastery_scores[skill] ?? 0;
              const isGap = result.gap_skills.includes(skill);
              return (
                <div className="list-item" key={skill} style={{ background: mastery >= 0.8 ? 'rgba(23, 121, 74, 0.05)' : 'rgba(255,255,255,0.5)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>{skill}</span>
                    <span className={`pill ${mastery >= 0.8 ? "good" : isGap ? "warn" : ""}`} style={{ fontSize: '0.75rem' }}>
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
        <div className="panel" style={{ alignSelf: 'stretch' }}>
          <span className="section-kicker">Learning Trajectory</span>
          <h3 style={{ marginBottom: 24, fontSize: '1.5rem' }}>Adaptive Step-by-Step Pathway</h3>
          <div className="roadmap">
            {result.reasoning.map((trace, idx) => {
              const course = result.course_map[trace.skill];
              return (
                <div 
                  className="roadmap-step animate-fade-in" 
                  key={trace.skill}
                  style={{ animationDelay: `${0.1 * idx}s`, paddingBottom: 48 }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 16 }}>
                    <div>
                      <div className="mono" style={{ fontSize: '0.65rem', color: 'var(--muted)', marginBottom: 4 }}>STEP 0{trace.position} // ID: {trace.skill.toUpperCase().replace(/\s/g, '_')}</div>
                      <div style={{ fontWeight: 800, fontSize: '1.4rem', color: 'var(--accent)' }}>{trace.skill}</div>
                    </div>
                    <button
                      className="button button-primary"
                      disabled={isRecomputing}
                      onClick={() => onMarkLearned(trace.skill)}
                      style={{ padding: '10px 20px', fontSize: '0.8rem', borderRadius: '12px' }}
                    >
                      {isRecomputing ? "Tracing..." : "Complete Milestone"}
                    </button>
                  </div>
                  <p className="muted" style={{ fontSize: '1.05rem', lineHeight: 1.6, marginBottom: 20 }}>{trace.reason}</p>
                  
                  {course && (
                    <div className="course-card" style={{ borderLeft: '4px solid var(--accent)', padding: '20px', background: 'rgba(255,255,255,0.5)' }}>
                      <div className="section-kicker" style={{ fontSize: '0.6rem', color: 'var(--accent)' }}>RECOMMENDED RESOURCE</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 8 }}>{course.name}</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                         <span className="pill" style={{ fontSize: '0.7rem' }}>Level: {course.difficulty}/10</span>
                         <span className="muted" style={{ fontSize: '0.8rem' }}>{course.url.split('/')[2]}</span>
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
