"use client";

import React from "react";

type Props = {
  pillars: Record<string, string[]>;
};

export function PillarDashboard({ pillars }: Props) {
  if (!pillars || Object.keys(pillars).length === 0) return null;

  return (
    <div className="pillar-dashboard mb-8 animate-fade-in stagger-2">
      <span className="section-kicker">Strategic Domains</span>
      <h3 className="mb-6">Skill Clusters</h3>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {Object.entries(pillars).map(([pillar, skills]) => (
          <div key={pillar} className="panel" style={{ padding: '20px', background: 'rgba(255,255,255,0.4)', border: '1px solid var(--line)' }}>
            <h4 className="mb-4" style={{ color: 'var(--accent)', fontSize: '0.95rem' }}>{pillar}</h4>
            <div className="flex" style={{ flexWrap: 'wrap', gap: '8px' }}>
              {skills.map((skill) => (
                <span 
                  key={skill} 
                  className="pill"
                  style={{ fontSize: '0.75rem', padding: '4px 10px' }}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
