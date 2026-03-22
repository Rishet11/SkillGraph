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
  mastered: "#1B7A48", // Green
  partial: "#F5A623",  // Orange
  critical_gap: "#E05A4E", // Red
  selected_path: "#2f78a8", // Blue
  unseen: "#9B9B9B" // Gray
};

const SkillNode = ({ data }: NodeProps) => {
  return (
    <div className="skill-node shadow-lg" style={{ 
      background: "white", 
      padding: "12px 16px", 
      borderRadius: "16px", 
      border: `2px solid ${COLORS[data.status] || '#ddd'}`,
      minWidth: "150px",
      textAlign: "center"
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{ fontWeight: "700", fontSize: "14px", color: "#1d1f33", marginBottom: "4px" }}>{data.label}</div>
      <div style={{ fontSize: "11px", color: "#666" }}>Mastery: {(data.mastery * 100).toFixed(0)}%</div>
      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
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
      style: { stroke: "#2f78a8", strokeWidth: 2, opacity: 0.4 },
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
        <Background color="#ddd" gap={24} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
