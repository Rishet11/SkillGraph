"use client";

import React from "react";

type Props = {
  pillars: Record<string, string[]>;
};

export function PillarDashboard({ pillars }: Props) {
  if (!pillars || Object.keys(pillars).length === 0) return null;

  return (
    <div className="pillar-dashboard mb-8">
      <h3 className="text-xl font-bold mb-4 text-[#1d1f33]/80">Skill Pillars</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(pillars).map(([pillar, skills]) => (
          <div key={pillar} className="pillar-card p-4 rounded-xl bg-white border border-[#1d1f33]/10 shadow-sm">
            <h4 className="font-bold text-[#C84B1E] mb-2">{pillar}</h4>
            <div className="flex flex-wrap gap-2">
              {skills.map((skill) => (
                <span 
                  key={skill} 
                  className="px-2 py-1 text-xs font-medium rounded-full bg-[#1d1f33]/5 text-[#1d1f33]/70 border border-[#1d1f33]/10"
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
