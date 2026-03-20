"use client";

import { AnalyzeResponse } from "../lib/types";

type Props = {
  graph: AnalyzeResponse["graph"];
};

const COLORS: Record<string, string> = {
  mastered: "#1B7A48",
  partial: "#F5A623",
  critical_gap: "#E05A4E",
  selected_path: "#C84B1E",
  unseen: "#9B9B9B"
};

export function GraphPanel({ graph }: Props) {
  const positioned = graph.nodes.map((node, index) => ({
    ...node,
    x: 110 + (index % 4) * 170,
    y: 90 + Math.floor(index / 4) * 120
  }));
  const nodeMap = new Map(positioned.map((node) => [node.id, node]));
  return (
    <div className="graph-wrap">
      <svg className="graph-svg" viewBox="0 0 760 500" role="img" aria-label="Skill graph">
        {graph.edges.map((edge) => {
          const source = nodeMap.get(edge.source);
          const target = nodeMap.get(edge.target);
          if (!source || !target) {
            return null;
          }
          return (
            <line
              key={`${edge.source}-${edge.target}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke="rgba(29,31,51,0.18)"
              strokeWidth="2"
            />
          );
        })}
        {positioned.map((node) => (
          <g key={node.id}>
            <circle cx={node.x} cy={node.y} r="28" fill={COLORS[node.status]} />
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
  return label.length > 18 ? `${label.slice(0, 17)}…` : label;
}

