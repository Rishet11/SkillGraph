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
    <section className="animate-fade-in stagger-1" style={{ marginTop: 40 }}>
      {/* Editorial Header */}
      <div className="panel" style={{ marginBottom: 24 }}>
        <span className="section-kicker">Analysis Outcome</span>
        <h2 style={{ fontSize: "2.5rem", marginBottom: 12 }}>{result.summary.headline}</h2>
        <p className="muted" style={{ fontSize: "1.15rem", marginBottom: 24 }}>{result.summary.explanation}</p>
        
        <PillarDashboard pillars={result.pillars} />

        <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <div className="score-card panel" style={{ padding: '24px' }}>
            <span className="section-kicker" style={{ fontSize: '0.65rem' }}>Skill Gaps</span>
            <div className="value">{result.gap_count}</div>
          </div>
          <div className="score-card panel" style={{ padding: '24px' }}>
            <span className="section-kicker" style={{ fontSize: '0.65rem' }}>Path Steps</span>
            <div className="value">{result.path.length}</div>
          </div>
          <div className="score-card panel" style={{ padding: '24px' }}>
            <span className="section-kicker" style={{ fontSize: '0.65rem' }}>Efficiency Gain</span>
            <div className="value">{result.metrics.redundant_modules_eliminated}%</div>
          </div>
        </div>
        
        <div className="flex" style={{ flexWrap: 'wrap', gap: '12px', marginTop: 24 }}>
          <span className="pill good">Domain: {result.domain.toUpperCase()}</span>
          <span className="pill">Trace coverage: {result.metrics.reasoning_trace_coverage}%</span>
          <span className="pill">Naive path: {result.metrics.naive_path_length}</span>
        </div>
      </div>

      <div className="three-panel">
        {/* Left: Skill Ledger */}
        <div className="panel">
          <span className="section-kicker">Skill Ledger</span>
          <h3 style={{ marginBottom: 20 }}>Inventory</h3>
          <div className="grid" style={{ gap: '12px' }}>
            {result.all_skills.map((skill) => {
              const mastery = result.mastery_scores[skill] ?? 0;
              const isGap = result.gap_skills.includes(skill);
              return (
                <div className="list-item" key={skill}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{skill}</span>
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

        {/* Middle: Schematic */}
        <div className="panel" style={{ padding: '20px' }}>
          <span className="section-kicker">Schematic</span>
          <h3 style={{ marginBottom: 16 }}>Dependency Map</h3>
          <p className="muted" style={{ fontSize: '0.85rem', marginBottom: 20 }}>
            Interactive trace of hierarchies. Green: Mastered | Orange: Gap | Blue: Pathway.
          </p>
          <GraphPanel graph={result.graph} />
        </div>

        {/* Right: Path */}
        <div className="panel">
          <span className="section-kicker">The Trajectory</span>
          <h3 style={{ marginBottom: 24 }}>Adaptive Roadmap</h3>
          <div className="roadmap animate-fade-in stagger-2">
            {result.reasoning.map((trace, idx) => {
              const course = result.course_map[trace.skill];
              return (
                <div 
                  className="roadmap-step animate-fade-in" 
                  key={trace.skill}
                  style={{ animationDelay: `${0.1 * idx}s` }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 12 }}>
                    <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--accent)' }}>
                      {trace.position}. {trace.skill}
                    </div>
                    <button
                      className="button button-secondary"
                      disabled={isRecomputing}
                      onClick={() => onMarkLearned(trace.skill)}
                      style={{ padding: '8px 14px', fontSize: '0.75rem', borderRadius: '12px' }}
                    >
                      {isRecomputing ? "..." : "Mark Learned"}
                    </button>
                  </div>
                  <p className="muted" style={{ fontSize: '0.95rem', marginBottom: 16 }}>{trace.reason}</p>
                  
                  {course && (
                    <div className="course-card">
                      <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: 6 }}>{course.name}</div>
                      <div className="muted" style={{ fontSize: '0.8rem' }}>
                        Diff: {course.difficulty}/10 · {course.url.split('/')[2]}
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
