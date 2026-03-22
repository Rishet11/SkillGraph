"use client";

import React from "react";

type Props = {
  pillars: Record<string, string[]>;
};

export function PillarDashboard({ pillars }: Props) {
  if (!pillars || Object.keys(pillars).length === 0) return null;

  return (
    <div className="animate-fade-in stagger-2">
      <span className="section-kicker">Strategic Domains</span>
      <h3 style={{ marginBottom: '24px' }}>Skill Clusters</h3>
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
        {Object.entries(pillars).map(([pillar, skills]) => (
          <div key={pillar} className="panel" style={{ padding: '24px' }}>
            <h4 style={{ color: 'var(--primary)', fontSize: '1.1rem', marginBottom: '16px' }}>{pillar}</h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {skills.map((skill) => (
                <span 
                  key={skill} 
                  className="pill"
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
