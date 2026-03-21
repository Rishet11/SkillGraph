"use client";

import React from "react";

type Props = {
  pillars: Record<string, string[]>;
};

export function PillarDashboard({ pillars }: Props) {
  if (!pillars || Object.keys(pillars).length === 0) return null;

  return (
    <div className="pillar-dashboard mb-8 animate-fade-in stagger-2">
      <h3 className="text-xl font-bold mb-4" style={{ color: 'var(--secondary)' }}>Skill Pillars</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(pillars).map(([pillar, skills]) => (
          <div key={pillar} className="pillar-card panel" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--panel-border)' }}>
            <h4 className="font-bold mb-3" style={{ color: 'var(--primary)', fontSize: '0.9rem' }}>{pillar}</h4>
            <div className="flex flex-wrap gap-2">
              {skills.map((skill) => (
                <span 
                  key={skill} 
                  className="pill"
                  style={{ fontSize: '0.7rem', background: 'rgba(139, 92, 246, 0.1)', borderColor: 'rgba(139, 92, 246, 0.2)' }}
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
