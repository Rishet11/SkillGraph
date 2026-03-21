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
      {/* Header Info */}
      <div className="panel" style={{ marginBottom: 24 }}>
        <p className="section-kicker">Analysis Outcome</p>
        <h2 style={{ fontSize: "2.5rem", marginBottom: 8 }}>{result.summary.headline}</h2>
        <p className="muted" style={{ fontSize: "1.1rem", marginBottom: 24 }}>{result.summary.explanation}</p>
        
        <PillarDashboard pillars={result.pillars} />

        <div className="score-grid">
          <div className="score-card panel">
            <div className="muted" style={{ fontSize: "0.9rem" }}>Skill Gaps</div>
            <div className="value">{result.gap_count}</div>
          </div>
          <div className="score-card panel">
            <div className="muted" style={{ fontSize: "0.9rem" }}>Path Steps</div>
            <div className="value">{result.path.length}</div>
          </div>
          <div className="score-card panel">
            <div className="muted" style={{ fontSize: "0.9rem" }}>Redundancy Eliminated</div>
            <div className="value">{result.metrics.redundant_modules_eliminated}%</div>
          </div>
        </div>
        
        <div className="badge-row" style={{ marginTop: 24 }}>
          <span className="pill good">Domain: {result.domain.toUpperCase()}</span>
          <span className="pill">Trace coverage: {result.metrics.reasoning_trace_coverage}%</span>
          <span className="pill">Naive path: {result.metrics.naive_path_length}</span>
        </div>
      </div>

      <div className="three-panel">
        {/* Left: Skill Status */}
        <div className="panel">
          <h3>Skill Inventory</h3>
          <div className="list">
            {result.all_skills.map((skill) => {
              const mastery = result.mastery_scores[skill] ?? 0;
              const isGap = result.gap_skills.includes(skill);
              return (
                <div className="list-item" key={skill}>
                  <div className="skill-row">
                    <span style={{ fontWeight: 600 }}>{skill}</span>
                    <span className={`pill ${mastery >= 0.8 ? "good" : isGap ? "warn" : ""}`}>
                      {(mastery * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="mastery-track">
                    <div className="mastery-fill" style={{ width: `${mastery * 100}%` }} />
                  </div>
                  <div className="pill-list">
                    {result.jd_data.required.includes(skill) && <span className="pill" style={{fontSize: '0.7rem'}}>required</span>}
                    {isGap && <span className="pill warn" style={{fontSize: '0.7rem'}}>gap</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Middle: Interactive Graph */}
        <div className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
             <h3>Skill Architecture</h3>
             <span className="pill" style={{ fontSize: '0.7rem', opacity: 0.7 }}>Interactive</span>
          </div>
          <p className="muted" style={{ fontSize: '0.85rem', marginBottom: 16 }}>
            Explore dependencies. Emerald nodes are mastered, Red are critical gaps, Violet is your personalized path.
          </p>
          <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: '24px', padding: '8px', border: '1px solid var(--panel-border)' }}>
            <GraphPanel graph={result.graph} />
          </div>
        </div>

        {/* Right: Path Reasoning */}
        <div className="panel">
          <h3>Adaptive Roadmap</h3>
          <div className="roadmap animate-fade-in stagger-2">
            {result.reasoning.map((trace, idx) => {
              const course = result.course_map[trace.skill];
              return (
                <div 
                  className="roadmap-step animate-fade-in" 
                  key={trace.skill}
                  style={{ animationDelay: `${0.1 * idx}s` }}
                >
                  <div className="skill-row" style={{ marginBottom: 12 }}>
                    <strong style={{ color: 'var(--secondary)' }}>
                      {trace.position}. {trace.skill}
                    </strong>
                    <button
                      className="button button-secondary small-button"
                      disabled={isRecomputing}
                      onClick={() => onMarkLearned(trace.skill)}
                      style={{ fontSize: '0.75rem' }}
                    >
                      {isRecomputing ? "..." : "Learn"}
                    </button>
                  </div>
                  <p className="muted" style={{ fontSize: '0.9rem', marginBottom: 12 }}>{trace.reason}</p>
                  
                  {course && (
                    <div className="course-card" style={{ background: 'var(--panel-strong)', border: '1px solid var(--panel-border)' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: 4 }}>{course.name}</div>
                      <div className="muted" style={{ fontSize: '0.75rem' }}>
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
