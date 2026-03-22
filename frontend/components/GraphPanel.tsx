"use client";

import React, { useMemo } from "react";
import ReactFlow, { 
  Background, 
  Controls, 
  Edge, 
  Node, 
  Position, 
  Handle,
  NodeProps 
} from "reactflow";
import "reactflow/dist/style.css";
import { AnalyzeResponse } from "../lib/types";

type Props = {
  graph: AnalyzeResponse["graph"];
};

const COLORS: Record<string, string> = {
  mastered: "#059669", // Success
  partial: "#D97706",  // Warning
  critical_gap: "#EA580C", // Primary
  selected_path: "#EA580C", // Primary
  unseen: "#94a3b8" // Muted
};

const SkillNode = ({ data }: NodeProps) => {
  return (
    <div className="skill-node" style={{ 
      background: "#FFFFFF", 
      padding: "16px", 
      borderRadius: "16px", 
      border: `2px solid var(--border)`,
      minWidth: "160px",
      textAlign: "center",
      boxShadow: "0 4px 12px rgba(15, 23, 42, 0.05)"
    }}>
      <Handle type="target" position={Position.Top} style={{ background: 'var(--border-strong)', width: '10px', height: '10px' }} />
      <div style={{ fontWeight: "700", fontSize: "14px", color: "var(--ink)", marginBottom: "8px", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>{data.label}</div>
      <div style={{ display: 'inline-block', background: 'var(--bg)', padding: '4px 12px', borderRadius: '999px', border: '1px solid var(--border)' }}>
        <div style={{ fontSize: "11px", color: COLORS[data.status] || "var(--ink)", fontWeight: 600 }}>Mastery: {(data.mastery * 100).toFixed(0)}%</div>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: 'var(--border-strong)', width: '10px', height: '10px' }} />
    </div>
  );
};

const nodeTypes = {
  skill: SkillNode,
};

export function GraphPanel({ graph }: Props) {
  const { nodes, edges } = useMemo(() => {
    const initialNodes: Node[] = graph.nodes.map((node, index) => ({
      id: node.id,
      type: "skill",
      data: { label: node.label, status: node.status, mastery: node.mastery },
      position: { 
        x: (index % 4) * 240, 
        y: Math.floor(index / 4) * 160 
      },
    }));

    const initialEdges: Edge[] = graph.edges.map((edge) => ({
      id: `e-${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      animated: true,
      style: { stroke: COLORS[edge.status] || "var(--border-strong)", strokeWidth: 2, opacity: 0.6 },
    }));

    return { nodes: initialNodes, edges: initialEdges };
  }, [graph]);

  return (
    <div style={{ height: "700px", width: "100%", background: "transparent", overflow: "hidden" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="var(--border-strong)" gap={24} size={1} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
