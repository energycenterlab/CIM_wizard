import { Node, Edge } from '@xyflow/react';
import { CompositeModel, CompositeNode, CompositeEdge } from '../slices/compositeModelsSlice';

// REMOVED: Frontend hardcoded models - now using backend-driven approach
// All model inputs/outputs are now fetched from backend and stored in node.data

export function buildCompositeFromSelection(
  allNodes: Node[],
  allEdges: Edge[],
  selectedIds: string[]
): CompositeModel | null {
  if (selectedIds.length < 2) {
    return null;
  }

  const selectedNodes = allNodes.filter(node => selectedIds.includes(node.id));
  const selectedEdges = allEdges.filter(edge => 
    selectedIds.includes(edge.source) && selectedIds.includes(edge.target)
  );

  if (selectedNodes.length === 0) {
    return null;
  }

  // Calculate relative positions (subtract minX/minY)
  const minX = Math.min(...selectedNodes.map(node => node.position.x));
  const minY = Math.min(...selectedNodes.map(node => node.position.y));

  // Create composite nodes - store EVERYTHING needed to reconstruct the node
  const compositeNodes: CompositeNode[] = selectedNodes.map(node => {
    const nodeData = node.data;
    const modelType = (nodeData.name || nodeData.type) as string;
    
    // Use inputs/outputs from backend (stored in node.data)
    const inputs = (nodeData.inputs || []) as string[];
    const outputs = (nodeData.outputs || []) as string[];

    return {
      id: node.id,
      modelDefId: modelType,
      type: node.type || 'parameditor', // Use the actual ReactFlow node type
      label: (nodeData.label || nodeData.name || modelType) as string,
      params: nodeData.params || {},
      width: node.width || 200,
      height: node.height || 120,
      relativeX: node.position.x - minX,
      relativeY: node.position.y - minY,
      inputs,
      outputs,
      // Store complete data object for full restoration
      data: {
        ...nodeData,
        // Ensure inputs/outputs are preserved
        inputs,
        outputs,
      },
      // Store any styling properties
      style: node.style,
      className: node.className,
    };
  });

  // Create composite edges - store complete edge information
  const compositeEdges: CompositeEdge[] = selectedEdges.map(edge => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.sourceHandle || '',
    targetHandle: edge.targetHandle || '',
    type: edge.type || 'custom',
    style: edge.style,
    markerEnd: edge.markerEnd,
    // Preserve edge data flags (e.g., isModelToModelEntityConnection)
    data: (edge as any).data,
  } as any));

  // Generate auto-suggested name
  const nodeLabels = selectedNodes
    .map(node => (node.data.name || node.data.type) as string)
    .filter(Boolean)
    .sort()
    .map(label => label.replace(/\s+/g, ''));
  
  const autoName = nodeLabels.join('+');

  return {
    id: `composite_${Date.now()}`,
    name: autoName,
    createdAt: new Date().toISOString(),
    nodes: compositeNodes,
    edges: compositeEdges,
  };
}

// Function to detect unused ports (ports that were NOT used in internal connections)
function detectUnusedPorts(composite: CompositeModel): { unusedInputs: string[], unusedOutputs: string[], allInputs: string[], allOutputs: string[] } {
  const allInputs = new Set<string>();
  const allOutputs = new Set<string>();
  const usedPorts = new Set<string>();
  
  const extractPortName = (handleId: string | undefined | null): string => {
    if (!handleId) return '';
    // handle ids are usually in the form "<nodeId>-<portName>"; fall back to the full string
    const idx = handleId.indexOf('-');
    if (idx === -1) return handleId;
    return handleId.slice(idx + 1);
  };

  // Collect all inputs and outputs from composite nodes
  composite.nodes.forEach(node => {
    if (node.inputs) node.inputs.forEach(input => allInputs.add(input));
    if (node.outputs) node.outputs.forEach(output => allOutputs.add(output));
  });

  // Track which ports are used in internal connections
  composite.edges.forEach(edge => {
    const sourceNode = composite.nodes.find(n => n.id === edge.source);
    const targetNode = composite.nodes.find(n => n.id === edge.target);
    
    if (sourceNode && targetNode) {
      // This is an internal connection - mark these ports as used
      const sourcePortName = extractPortName(edge.sourceHandle);
      const targetPortName = extractPortName(edge.targetHandle);
      if (sourcePortName && sourceNode.outputs?.includes(sourcePortName)) {
        usedPorts.add(sourcePortName);
      }
      if (targetPortName && targetNode.inputs?.includes(targetPortName)) {
        usedPorts.add(targetPortName);
      }
    }
  });

  // Unused ports are those that exist but are NOT used in internal connections
  // These are the ports that were available but not connected within the composite
  const unusedInputs = Array.from(allInputs).filter(input => !usedPorts.has(input));
  const unusedOutputs = Array.from(allOutputs).filter(output => !usedPorts.has(output));


  return {
    unusedInputs,
    unusedOutputs,
    allInputs: Array.from(allInputs),
    allOutputs: Array.from(allOutputs)
  };
}

export function instantiateComposite(
  composite: CompositeModel,
  origin: { x: number; y: number } = { x: 100, y: 100 }
): { nodes: Node[]; edges: Edge[] } {
  
  const compositeGroupId = `composite_group_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  // Detect unused ports (ports that were NOT used in internal connections)
  const { unusedInputs, unusedOutputs, allInputs, allOutputs } = detectUnusedPorts(composite);
  
  // Create a single composite block node instead of individual nodes
  const compositeBlockId = `composite_block_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  const compositeBlock: Node = {
    id: compositeBlockId,
    type: 'CompositeBlock',
    position: origin,
    data: {
      label: composite.name,
      compositeName: composite.name,
      compositeGroupId: compositeGroupId,
      // Store the original composite data for potential expansion
      originalComposite: composite,
      nodes: composite.nodes,
      edges: composite.edges,
      // Port configuration - show unused ports by default
      unusedInputs,
      unusedOutputs,
      allInputs,
      allOutputs,
      exposedPorts: {
        inputs: unusedInputs,
        outputs: unusedOutputs
      }
    },
    width: 350,
    height: 160
  };

  // Return only the composite block - no individual nodes or internal edges
  return {
    nodes: [compositeBlock],
    edges: [] // No edges for the composite block itself
  };
}

export function deleteCompositeGroup(
  compositeGroupId: string,
  allNodes: Node[],
  allEdges: Edge[]
): { remainingNodes: Node[]; remainingEdges: Edge[] } {
  // Find all nodes in this composite group
  const nodesToDelete = allNodes.filter(node => node.data?.compositeGroupId === compositeGroupId);
  const nodeIdsToDelete = new Set(nodesToDelete.map(node => node.id));
  
  // Remove nodes in the composite group
  const remainingNodes = allNodes.filter(node => !nodeIdsToDelete.has(node.id));
  
  // Remove edges connected to deleted nodes
  const remainingEdges = allEdges.filter(edge => 
    !nodeIdsToDelete.has(edge.source) && !nodeIdsToDelete.has(edge.target)
  );
  
  return { remainingNodes, remainingEdges };
}

export function generateCompositeName(selectedNodes: Node[]): string {
  const nodeLabels = selectedNodes
    .map(node => (node.data.name || node.data.type) as string)
    .filter(Boolean)
    .sort()
    .map(label => label.replace(/\s+/g, ''));
  
  return nodeLabels.join('+');
}
