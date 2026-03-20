"use client";

import { AnalyzeResponse } from "../lib/types";

type Props = {
  graph: AnalyzeResponse["graph"];
};

const COLORS: Record<string, string> = {
  current_skill: "#2f78a8",
  target_skill: "#1d1f33",
  gap_skill: "#c45d28",
  prerequisite: "#7d6c3f",
  recommended_course: "#17794a"
};

export function GraphPanel({ graph }: Props) {
  const positions = graph.nodes.map((node, index) => {
    const column = index % 3;
    const row = Math.floor(index / 3);
    return {
      ...node,
      x: 120 + column * 220,
      y: 90 + row * 120
    };
  });

  const nodeMap = new Map(positions.map((node) => [node.id, node]));

  return (
    <div className="graph-wrap">
      <svg className="graph-svg" viewBox="0 0 760 480" role="img" aria-label="Skill graph">
        {graph.edges.map((edge, index) => {
          const source = nodeMap.get(edge.source);
          const target = nodeMap.get(edge.target);
          if (!source || !target) {
            return null;
          }
          return (
            <g key={`${edge.source}-${edge.target}-${index}`}>
              <line
                x1={source.x}
                y1={source.y}
                x2={target.x}
                y2={target.y}
                stroke="rgba(29,31,51,0.22)"
                strokeWidth="2"
              />
            </g>
          );
        })}
        {positions.map((node) => (
          <g key={node.id}>
            <circle cx={node.x} cy={node.y} r="28" fill={COLORS[node.type]} />
            <text x={node.x} y={node.y + 48} textAnchor="middle" fontSize="12" fill="#1d1f33">
              {truncate(node.label)}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function truncate(label: string) {
  return label.length > 16 ? `${label.slice(0, 15)}…` : label;
}

