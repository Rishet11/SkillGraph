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
  mastered: "#10b981", // Emerald
  partial: "#f59e0b",  // Warn/Amber
  critical_gap: "#ef4444", // Error/Red
  selected_path: "#8b5cf6", // Violet/Primary
  unseen: "#475569" // Slate
};

// Custom Node Component for a premium look
const SkillNode = ({ data }: NodeProps) => {
  return (
    <div className="skill-node shadow-xl" style={{ 
      background: "rgba(30, 41, 59, 0.9)", 
      padding: "12px 18px", 
      borderRadius: "16px", 
      border: `1px solid ${COLORS[data.status] || 'rgba(255,255,255,0.1)'}`,
      minWidth: "140px",
      textAlign: "center",
      backdropFilter: "blur(8px)",
      boxShadow: `0 0 15px ${COLORS[data.status]}22`
    }}>
      <Handle type="target" position={Position.Top} style={{ background: COLORS[data.status] }} />
      <div style={{ fontWeight: "700", fontSize: "14px", color: "white", marginBottom: "4px" }}>{data.label}</div>
      <div style={{ fontSize: "11px", color: "rgba(255,255,255,0.6)" }}>Mastery: {data.mastery.toFixed(2)}</div>
      <Handle type="source" position={Position.Bottom} style={{ background: COLORS[data.status] }} />
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
        x: (index % 4) * 220, 
        y: Math.floor(index / 4) * 160 
      },
    }));

    const initialEdges: Edge[] = graph.edges.map((edge) => ({
      id: `e-${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      animated: true,
      style: { stroke: "rgba(139, 92, 246, 0.4)", strokeWidth: 2 },
    }));

    return { nodes: initialNodes, edges: initialEdges };
  }, [graph]);

  return (
    <div style={{ height: "450px", width: "100%", background: "transparent", borderRadius: "24px", overflow: "hidden" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="rgba(255,255,255,0.05)" gap={24} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
