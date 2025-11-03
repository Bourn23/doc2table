import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Maximize2, Minimize2, Download } from 'lucide-react';
import { GraphGenerationResponse } from '../types';
import { colors, typography } from '../styles/designTokens';
import * as d3 from 'd3';

interface GraphVisualizationProps {
  graphData: GraphGenerationResponse;
  onClose: () => void;
}

interface PositionedNode {
  id: string;
  type: string;
  properties: any;
  x?: number; // D3 will initialize these
  y?: number; // D3 will initialize these
  fx?: number | null; // Fixed x position (for dragging)
  fy?: number | null; // Fixed y position (for dragging)
}


/**
 * GraphVisualization Component
 * Displays knowledge graph with nodes and relationships
 * Features:
 * - Force-directed layout for automatic clustering
 * - Interactive draggable nodes
 * - Export as SVG or PNG
 */
export const GraphVisualization: React.FC<GraphVisualizationProps> = ({ graphData, onClose }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [nodePositions, setNodePositions] = useState<PositionedNode[]>([]);
  const [draggedNode, setDraggedNode] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [currentTransform, setCurrentTransform] = useState(d3.zoomIdentity);
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const gRef = useRef<SVGGElement>(null);

  const simulationRef = useRef<d3.Simulation<PositionedNode, any> | null>(null);
  
  // Use useEffect to run the D3 force simulation
  useEffect(() => {
    // Make copies to avoid mutating the original props data
    const nodes: PositionedNode[] = graphData.nodes.map(d => ({ ...d }));
    const links = graphData.relationships.map(d => ({ source: d.source.id, target: d.target.id, type: d.type }));

    simulationRef.current = d3.forceSimulation(nodes)
      // Attraction force: pulls connected nodes together
      .force("link", d3.forceLink(links)
        .id((d: any) => d.id) // Tell D3 how to identify nodes for linking
        .distance(90) // Set the ideal distance between connected nodes
      )
      // Repulsion force: pushes all nodes away from each other
      .force("charge", d3.forceManyBody().strength(-80))
      // Centering force: pulls the whole graph towards the center of the viewbox
      .force("center", d3.forceCenter(400, 300))
      .on("tick", () => {
        // Update state with new positions from simulation
        setNodePositions([...nodes]);
      });

    // Cleanup function to stop the simulation when the component unmounts
    return () => {
      simulationRef.current?.stop();
    };
  }, [graphData]); // Re-run the simulation if the graphData changes

  // Setup D3 zoom behavior
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    
    const zoomBehavior = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 5]) // Min 0.2x zoom, Max 5x zoom
      .filter((event) => {
        // Prevent zoom from starting if the event target is part of a node group
        // This allows node dragging to work without interference.
        const target = event.target as SVGElement;
        return !target.closest('.node-group');
      })
      .on("zoom", (event) => {
        if (!draggedNode) { // only pan if not dragging a node
          setCurrentTransform(event.transform);
        }
      });

    svg.call(zoomBehavior);

    // Disable zoom on double-click
    svg.on("dblclick.zoom", null);
    
  }, [draggedNode]); // Re-attach zoom behavior if draggedNode state changes (though not strictly necessary here)

  // Find node by id from the state
  const findNodeById = (id: string) => {
    return nodePositions.find(n => n.id === id);
  };

  const handleNodeDragStart = (event: React.MouseEvent<SVGCircleElement>, nodeId: string) => {
    event.stopPropagation(); // <-- This is the key! Stops the zoom behavior from starting.
    const simulation = simulationRef.current;
    if (!simulation) return;

    const subject = nodePositions.find(n => n.id === nodeId);
    if (!subject) return;

    // "Reheat" the simulation and set the node's fixed position
    // simulation.alphaTarget(0.3).restart();
    subject.fx = subject.x;
    subject.fy = subject.y;

    setDraggedNode(nodeId);
  };

  const handleNodeDrag = (event: React.MouseEvent<SVGSVGElement>) => {
    const simulation = simulationRef.current;
    if (!draggedNode || !simulation) return;
    
    const subject = nodePositions.find(n => n.id === draggedNode);
    if (!subject) return;

    // Calculate mouse position in the transformed SVG space
    const pt = svgRef.current?.createSVGPoint();
    if (!pt) return;
    pt.x = event.clientX;
    pt.y = event.clientY;
    
    // Get the inverse of the screen CTM
    const svgInverseMatrix = svgRef.current?.getScreenCTM()?.inverse();
    if (!svgInverseMatrix) return;
    
    const svgP = pt.matrixTransform(svgInverseMatrix);
    const transformedX = (svgP.x - currentTransform.x) / currentTransform.k;
    const transformedY = (svgP.y - currentTransform.y) / currentTransform.k;

    // Update the node's fixed position on drag
    subject.fx = transformedX;
    subject.fy = transformedY;
    
    // Also update its x/y for immediate render
    subject.x = transformedX;
    subject.y = transformedY;

    // Manually trigger a state update to re-render
    setNodePositions([...nodePositions]);
  };

  const handleNodeDragEnd = () => {
    const simulation = simulationRef.current;
    if (!draggedNode || !simulation) return;

    const subject = nodePositions.find(n => n.id === draggedNode);

    // "Cool down" the simulation and release the node's fixed position
    // simulation.alphaTarget(0);
    if (subject) {
      subject.fx = null;
      subject.fy = null;
    }
    
    setDraggedNode(null);
  };

  const exportAsSVG = () => {
    if (!svgRef.current) return;

    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    const downloadLink = document.createElement('a');
    downloadLink.href = svgUrl;
    downloadLink.download = 'knowledge-graph.svg';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
    URL.revokeObjectURL(svgUrl);
  };

  const exportAsPNG = () => {
    if (!svgRef.current) return;

    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    // Use viewBox dimensions for better scaling
    const viewBox = svgRef.current.viewBox.baseVal;
    canvas.width = viewBox.width * 2; // Increase resolution
    canvas.height = viewBox.height * 2;

    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);

      canvas.toBlob((blob) => {
        if (!blob) return;
        const pngUrl = URL.createObjectURL(blob);
        const downloadLink = document.createElement('a');
        downloadLink.href = pngUrl;
        downloadLink.download = 'knowledge-graph.png';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(pngUrl);
      });
    };

    img.src = url;
  };
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className={`relative rounded-xl border-2 overflow-hidden ${
            isFullscreen ? 'w-full h-full' : 'w-[90vw] h-[80vh] max-w-6xl'
          }`}
          style={{
            backgroundColor: colors.midnight.deep,
            borderColor: colors.insight.bloom,
          }}
          ref={containerRef}
        >
          {/* Header */}
          <div
            className="px-6 py-4 border-b flex items-center justify-between"
            style={{
              borderColor: `${colors.silver.warm}20`,
              backgroundColor: colors.midnight.mid,
            }}
          >
            <div>
              <h2
                style={{
                  fontSize: typography.sizes.h3,
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                }}
              >
                Knowledge Graph
              </h2>
              <p
                style={{
                  fontSize: typography.sizes.caption,
                  color: colors.text.tertiary,
                  marginTop: '4px',
                }}
              >
                {graphData.nodes.length} nodes, {graphData.relationships.length} relationships
              </p>
            </div>

            <div className="flex items-center gap-2">
              {/* Export dropdown */}
              <div className="relative group">
                <button
                  className="p-2 rounded-lg transition-all hover:scale-110 flex items-center gap-1"
                  style={{
                    backgroundColor: `${colors.hermes.cyan}20`,
                    color: colors.hermes.cyan,
                  }}
                >
                  <Download className="w-5 h-5" />
                  <span style={{ fontSize: typography.sizes.caption }}>Export</span>
                </button>
                {/* Dropdown menu */}
                <div className="absolute right-0 mt-2 w-40 rounded-lg border shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50"
                  style={{
                    backgroundColor: colors.midnight.mid,
                    borderColor: colors.hermes.cyan,
                  }}
                >
                  <button
                    onClick={exportAsSVG}
                    className="w-full px-4 py-2 text-left hover:bg-white/10 transition-colors rounded-t-lg"
                    style={{
                      color: colors.text.primary,
                      fontSize: typography.sizes.bodySmall,
                    }}
                  >
                    Download as SVG
                  </button>
                  <button
                    onClick={exportAsPNG}
                    className="w-full px-4 py-2 text-left hover:bg-white/10 transition-colors rounded-b-lg"
                    style={{
                      color: colors.text.primary,
                      fontSize: typography.sizes.bodySmall,
                    }}
                  >
                    Download as PNG
                  </button>
                </div>
              </div>

              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-2 rounded-lg transition-all hover:scale-110"
                style={{
                  backgroundColor: `${colors.insight.bloom}20`,
                  color: colors.insight.bloom,
                }}
              >
                {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
              </button>
              <button
                onClick={onClose}
                className="p-2 rounded-lg transition-all hover:scale-110"
                style={{
                  backgroundColor: `${colors.text.tertiary}20`,
                  color: colors.text.tertiary,
                }}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Graph Canvas */}
          <div className="relative w-full h-full overflow-hidden" style={{ backgroundColor: colors.midnight.light }}>
            <svg
              ref={svgRef}
              width="100%"
              height="100%"
              viewBox="0 0 800 600"
              preserveAspectRatio="xMidYMid meet"
              onMouseMove={handleNodeDrag}
              onMouseUp={handleNodeDragEnd}
              onMouseLeave={handleNodeDragEnd}
              style={{ cursor: draggedNode ? 'grabbing' : 'grab' }}
            >
            <g ref={gRef} transform={currentTransform.toString()}>
              {/* Draw relationships (edges) */}
              <g>
                {graphData.relationships.map((rel, idx) => {
                  const sourceNode = findNodeById(rel.source.id);
                  const targetNode = findNodeById(rel.target.id);

                  if (!sourceNode || !targetNode) return null;

                  return (
                    <g key={`${rel.source.id}-${rel.target.id}-${idx}`}>
                      <line
                        x1={sourceNode.x}
                        y1={sourceNode.y}
                        x2={targetNode.x}
                        y2={targetNode.y}
                        stroke={colors.hermes.cyan}
                        strokeWidth="2"
                        strokeOpacity="0.4"
                      />
                      {/* Relationship label */}
                      <text
                        x={(sourceNode.x + targetNode.x) / 2}
                        y={(sourceNode.y + targetNode.y) / 2}
                        fill={colors.text.tertiary}
                        fontSize="10"
                        textAnchor="middle"
                      >
                        {rel.type}
                      </text>
                    </g>
                  );
                })}
              </g>
            

              {/* Draw nodes */}
              <g>
                {nodePositions.map((node) => (
                  <g key={node.id} className="node-group"> {/* <-- CLASS ADDED HERE */}
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r="30"
                      fill={colors.insight.bloom}
                      fillOpacity="0.2"
                      stroke={colors.insight.bloom}
                      strokeWidth="2"
                      style={{ cursor: 'grab' }}
                      onClick={() => setSelectedNode(node)}
                      //
                      // --- THIS IS THE FIX ---
                      //
                      onMouseDown={(e) => handleNodeDragStart(e, node.id)}
                    />
                    <text
                      x={node.x}
                      y={node.y}
                      fill={colors.text.primary}
                      fontSize="12"
                      fontWeight="medium"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="pointer-events-none"
                    >
                      {node.id.length > 15 ? node.id.substring(0, 12) + '...' : node.id}
                    </text>
                    {/* Node type label */}
                    <text
                      x={node.x}
                      y={node.y + 45} // Positioned below the main label
                      fill={colors.text.tertiary}
                      fontSize="9"
                      textAnchor="middle"
                      className="pointer-events-none"
                    >
                      {node.type}
                    </text>
                  </g>
                ))}
                </g>
              </g>
            </svg>

            {/* Selected node info panel */}
            <AnimatePresence>
              {selectedNode && (
                <motion.div
                  initial={{ x: 300, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  exit={{ x: 300, opacity: 0 }}
                  className="absolute top-4 right-4 p-4 rounded-lg border max-w-sm"
                  style={{
                    backgroundColor: colors.midnight.mid,
                    borderColor: colors.insight.bloom,
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3
                      style={{
                        fontSize: typography.sizes.bodyLarge,
                        fontWeight: typography.weights.medium,
                        color: colors.text.primary,
                      }}
                    >
                      {selectedNode.id}
                    </h3>
                    <button
                      onClick={() => setSelectedNode(null)}
                      className="p-1 rounded hover:bg-white/10"
                    >
                      <X className="w-4 h-4" style={{ color: colors.text.tertiary }} />
                    </button>
                  </div>

                  <div
                    className="px-2 py-1 rounded-full inline-block mb-3"
                    style={{
                      backgroundColor: `${colors.insight.bloom}20`,
                      color: colors.insight.bloom,
                      fontSize: typography.sizes.caption,
                    }}
                  >
                    {selectedNode.type}
                  </div>

                  {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                    <div>
                      <p
                        style={{
                          fontSize: typography.sizes.bodySmall,
                          color: colors.text.secondary,
                          marginBottom: '8px',
                        }}
                      >
                        Properties:
                      </p>
                      <div className="space-y-1">
                        {Object.entries(selectedNode.properties).map(([key, value]) => (
                          <div
                            key={key}
                            className="flex items-start gap-2"
                            style={{
                              fontSize: typography.sizes.caption,
                              color: colors.text.tertiary,
                            }}
                          >
                            <span style={{ color: colors.hermes.cyan }}>{key}:</span>
                            <span>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Legend & Instructions */}
          <div
            className="absolute bottom-4 left-4 p-3 rounded-lg border space-y-2"
            style={{
              backgroundColor: `${colors.midnight.mid}90`,
              borderColor: `${colors.silver.warm}20`,
            }}
          >
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded-full border-2"
                  style={{
                    backgroundColor: `${colors.insight.bloom}20`,
                    borderColor: colors.insight.bloom,
                  }}
                />
                <span style={{ fontSize: typography.sizes.caption, color: colors.text.secondary }}>
                  Entity
                </span>
              </div>
              <div className="flex items-center gap-2">
                <div
                  className="w-8 h-0.5"
                  style={{ backgroundColor: colors.hermes.cyan, opacity: 0.4 }}
                />
                <span style={{ fontSize: typography.sizes.caption, color: colors.text.secondary }}>
                  Relationship
                </span>
              </div>
            </div>
            <div
              className="text-xs pt-2 border-t"
              style={{
                color: colors.text.tertiary,
                borderColor: `${colors.silver.warm}10`,
              }}
            >
              💡 Drag nodes to rearrange • Click nodes for details
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};