"use client";

import { AnalyzeResponse } from "../lib/types";
import { GraphPanel } from "./GraphPanel";

type Props = {
  result: AnalyzeResponse;
};

export function ResultDashboard({ result }: Props) {
  return (
    <section className="grid" style={{ marginTop: 26 }}>
      <div className="panel">
        <p className="section-kicker">Analysis Outcome</p>
        <h2>{result.summary.headline}</h2>
        <p className="muted">{result.summary.explanation}</p>
        <div className="score-grid">
          <div className="score-card">
            <div className="muted">Fit score</div>
            <div className="value">{result.fit_score}</div>
          </div>
          <div className="score-card">
            <div className="muted">Confidence</div>
            <div className="value">{result.confidence}</div>
          </div>
          <div className="score-card">
            <div className="muted">Learning steps</div>
            <div className="value">{result.learning_path.length}</div>
          </div>
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

      <div className="breakdown-grid">
        <div className="panel">
          <h3>Matched Skills</h3>
          <div className="list">
            {result.matched_skills.length ? (
              result.matched_skills.map((skill) => (
                <div className="list-item" key={skill.skill_id}>
                  <strong>
                    {skill.label} · {skill.mastery_score}
                  </strong>
                  <div className="pill-list">
                    <span className={`pill ${skill.status === "matched" ? "good" : ""}`}>{skill.status}</span>
                  </div>
                  <p className="muted">{skill.reason}</p>
                </div>
              ))
            ) : (
              <p className="muted">No strong alignment yet.</p>
            )}
          </div>
        </div>

        <div className="panel">
          <h3>Missing Skills</h3>
          <div className="list">
            {result.missing_skills.length ? (
              result.missing_skills.map((skill) => (
                <div className="list-item" key={skill.skill_id}>
                  <strong>{skill.label}</strong>
                  <div className="pill-list">
                    <span className="pill warn">{skill.gap_type}</span>
                    {skill.missing_prerequisites.map((item) => (
                      <span className="pill" key={item}>
                        needs {item.replaceAll("_", " ")}
                      </span>
                    ))}
                  </div>
                  <p className="muted">{skill.reason}</p>
                </div>
              ))
            ) : (
              <p className="muted">No major role gaps detected.</p>
            )}
          </div>
        </div>
      </div>

      <div className="main-grid grid">
        <div className="panel">
          <h3>Skill Graph</h3>
          <p className="muted">
            Current skills, target expectations, prerequisites, and recommendations are connected
            into one explorable map.
          </p>
          <GraphPanel graph={result.graph} />
        </div>

        <div className="panel">
          <h3>Learning Path</h3>
          <div className="roadmap">
            {result.learning_path.map((step) => (
              <div className="roadmap-step" key={step.skill_id}>
                <strong>
                  {step.order}. {step.goal}
                </strong>
                <p className="muted">{step.why_now}</p>
                <div className="pill-list">
                  {step.recommended_courses.length ? (
                    step.recommended_courses.map((course) => (
                      <a className="pill good" href={course.url} key={course.course_id} target="_blank" rel="noreferrer">
                        {course.title} · {course.duration}
                      </a>
                    ))
                  ) : (
                    <span className="pill">Add project practice for this skill</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="main-grid grid">
        <div className="panel">
          <h3>Extracted Resume Evidence</h3>
          <div className="list">
            {result.resume_skills.map((skill) => (
              <div className="list-item" key={skill.skill_id}>
                <strong>
                  {skill.label} · {skill.mastery_score}
                </strong>
                <p className="muted">Source section: {skill.source_section}</p>
                <div className="pill-list">
                  {skill.evidence_snippets.map((snippet) => (
                    <span className="pill" key={snippet}>
                      {snippet}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h3>Judge-Friendly Explainability</h3>
          <div className="formula">
            fit_score = weighted matched skill evidence - missing required skill penalty + adjacency credit
          </div>
          <p className="muted" style={{ marginTop: 16 }}>
            This MVP uses deterministic scoring first. LLM wording can be added later, but the
            scores, graph, and recommendations remain reproducible.
          </p>
          <div className="badge-row">
            <span className="pill good">Deterministic core</span>
            <span className="pill">Confidence-aware</span>
            <span className="pill warn">Local-first demo</span>
          </div>
        </div>
      </div>
    </section>
  );
}

