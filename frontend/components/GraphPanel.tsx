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
  mastered: "#1B7A48",
  partial: "#F5A623",
  critical_gap: "#E05A4E",
  selected_path: "#C84B1E",
  unseen: "#9B9B9B"
};

// Custom Node Component for a premium look
const SkillNode = ({ data }: NodeProps) => {
  return (
    <div className="skill-node shadow-lg" style={{ 
      background: "white", 
      padding: "10px 15px", 
      borderRadius: "12px", 
      border: `2px solid ${COLORS[data.status] || '#ddd'}`,
      minWidth: "120px",
      textAlign: "center"
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      <div style={{ fontWeight: "bold", fontSize: "13px", color: "#1d1f33" }}>{data.label}</div>
      <div style={{ fontSize: "10px", color: "#666" }}>Mastery: {data.mastery.toFixed(2)}</div>
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
        x: (index % 4) * 200, 
        y: Math.floor(index / 4) * 150 
      },
    }));

    const initialEdges: Edge[] = graph.edges.map((edge) => ({
      id: `e-${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      animated: true,
      style: { stroke: "rgba(200, 75, 30, 0.3)", strokeWidth: 2 },
    }));

    return { nodes: initialNodes, edges: initialEdges };
  }, [graph]);

  return (
    <div style={{ height: "450px", width: "100%", background: "#f8f9fa", borderRadius: "16px", overflow: "hidden", border: "1px solid rgba(29,31,51,0.1)" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        // zoomOnScroll={false}
        // panOnScroll={true}
      >
        <Background color="#aaa" gap={20} />
        <Controls />
      </ReactFlow>
    </div>
  );
}
