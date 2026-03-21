"use client";

import { AnalyzeResponse } from "../lib/types";
import { GraphPanel } from "./GraphPanel";

type Props = {
  result: AnalyzeResponse;
  onMarkLearned: (skill: string) => void;
  isRecomputing: boolean;
};

export function ResultDashboard({ result, onMarkLearned, isRecomputing }: Props) {
  return (
    <section className="grid" style={{ marginTop: 26 }}>
      <div className="panel">
        <p className="section-kicker">Analysis Outcome</p>
        <h2>{result.summary.headline}</h2>
        <p className="muted">{result.summary.explanation}</p>
        <div className="score-grid">
          <div className="score-card">
            <div className="muted">Gap count</div>
            <div className="value">{result.gap_count}</div>
          </div>
          <div className="score-card">
            <div className="muted">Recommended path</div>
            <div className="value">{result.path.length}</div>
          </div>
          <div className="score-card">
            <div className="muted">Redundant modules removed</div>
            <div className="value">{result.metrics.redundant_modules_eliminated}%</div>
          </div>
        </div>
        <div className="badge-row" style={{ marginTop: 18 }}>
          <span className="pill">Domain: {result.domain.toUpperCase()}</span>
          <span className="pill">Trace coverage: {result.metrics.reasoning_trace_coverage}%</span>
          <span className="pill">Naive path: {result.metrics.naive_path_length}</span>
          <span className="pill">Missing: {result.gap_report.missing.length}</span>
          <span className="pill">Weak: {result.gap_report.weak.length}</span>
          <span className="pill">Met: {result.gap_report.met.length}</span>
        </div>
        {!!result.warnings.length && (
          <div className="badge-row" style={{ marginTop: 18 }}>
            {result.warnings.map((warning) => (
              <span className="pill warn" key={warning}>
                {warning}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="three-panel">
        <div className="panel">
          <h3>Skill Panel</h3>
          <div className="list">
            {result.all_skills.map((skill) => {
              const mastery = result.mastery_scores[skill] ?? 0;
              const inPath = result.path.includes(skill);
              const isGap = result.gap_skills.includes(skill);
              return (
                <div className="list-item" key={skill}>
                  <div className="skill-row">
                    <strong>{skill}</strong>
                    <span className={`pill ${mastery >= 0.8 ? "good" : isGap ? "warn" : ""}`}>
                      {mastery.toFixed(2)}
                    </span>
                  </div>
                  <div className="mastery-track">
                    <div className="mastery-fill" style={{ width: `${mastery * 100}%` }} />
                  </div>
                  <div className="pill-list">
                    {result.jd_data.required.includes(skill) && <span className="pill">required</span>}
                    {result.jd_data.preferred.includes(skill) && <span className="pill">preferred</span>}
                    {inPath && <span className="pill warn">path</span>}
                    {isGap && <span className="pill warn">gap</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="panel">
          <h3>Graph Panel</h3>
          <p className="muted">
            Green is mastered, yellow is partial, red is a critical gap, and orange is the selected learning path.
          </p>
          <GraphPanel graph={result.graph} />
        </div>

        <div className="panel">
          <h3>Path + Reasoning</h3>
          <div className="roadmap">
            {result.reasoning.map((trace) => {
              const course = result.course_map[trace.skill];
              return (
                <div className="roadmap-step" key={trace.skill}>
                  <div className="skill-row">
                    <strong>
                      {trace.position}. {trace.skill}
                    </strong>
                    <button
                      className="button button-secondary small-button"
                      disabled={isRecomputing}
                      onClick={() => onMarkLearned(trace.skill)}
                    >
                      {isRecomputing ? "Updating..." : "Mark learned"}
                    </button>
                  </div>
                  <p className="muted">{trace.reason}</p>
                  <div className="pill-list">
                    <span className="pill">mastery {trace.mastery.toFixed(2)}</span>
                    <span className="pill">required {trace.required_level.toFixed(2)}</span>
                    <span className="pill">gap {trace.gap.toFixed(2)}</span>
                    <span className="pill">priority {trace.priority_score.toFixed(2)}</span>
                    <span className="pill">depth {trace.downstream_depth}</span>
                    {trace.required_by_jd && <span className="pill good">required</span>}
                    {trace.preferred_by_jd && <span className="pill">preferred</span>}
                  </div>
                  <div className="pill-list" style={{ marginTop: 10 }}>
                    {trace.reason_codes.map((code) => (
                      <span className="pill" key={`${trace.skill}-${code}`}>
                        {code}
                      </span>
                    ))}
                  </div>
                  <div className="pill-list" style={{ marginTop: 10 }}>
                    <span className="pill">JD: {trace.evidence.jd_signal}</span>
                    <span className="pill">mentions: {trace.evidence.resume_mentions}</span>
                    {trace.evidence.resume_sections.map((section) => (
                      <span className="pill" key={`${trace.skill}-src-${section}`}>
                        src {section}
                      </span>
                    ))}
                  </div>
                  {trace.evidence.resume_snippets.length > 0 && (
                    <p className="muted">Resume evidence: {trace.evidence.resume_snippets.join(" | ")}</p>
                  )}
                  {trace.evidence.jd_snippets.length > 0 && (
                    <p className="muted">JD evidence: {trace.evidence.jd_snippets.join(" | ")}</p>
                  )}
                  <div className="pill-list" style={{ marginTop: 10 }}>
                    {trace.unlocks.map((unlock) => (
                      <span className="pill" key={unlock}>
                        unlocks {unlock}
                      </span>
                    ))}
                  </div>
                  <div className="course-card">
                    <strong>{course?.name ?? "No course available"}</strong>
                    <p className="muted">
                      Covers: {course ? course.covers.join(", ") : trace.skill} · Difficulty{" "}
                      {course?.difficulty ?? 0}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
