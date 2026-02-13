import React, { useEffect } from 'react';
import { BaseEdge, getSmoothStepPath, useStore } from '@xyflow/react';

const CustomEdge = ({
  id,
  source,
  target,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  sourceHandle,
  targetHandle,
  style = {},
  data,
  selected,
}) => {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
    borderRadius: 16, // rounded corners for tidier look
    offset: 8, // small offset to avoid hugging nodes too tightly
  });

  // Hover state (only highlight when the cursor touches the stroke)
  const [hovered, setHovered] = React.useState(false);

  // Get edge from store to ensure we have sourceHandle and targetHandle
  const edge = useStore((store) => store.edges.find((e) => e.id === id));

  // Edge styling
  let strokeDasharray = '';
  let strokeColor = style.stroke || '#1E3A8A'; // default blue
  
  // Dotted blue for batch → model
  if (data?.isBatchToModel) {
    strokeDasharray = '8,4';
    strokeColor = '#0069FF';
  }
  // Dotted pink for model ↔ model entity connection
  if (data?.isModelToModelEntityConnection) {
    strokeDasharray = '8,4';
    strokeColor = '#FF69B4';
  }

  // Light by default; vivid on hover/selected
  const isActive = hovered || !!selected;
  const strokeOpacity = isActive ? 1 : 0.2;

  // Highlight badges when edge is hovered/selected
  useEffect(() => {
    // Get handle IDs from edge object or props
    const sourceHandleId = edge?.sourceHandle || sourceHandle;
    const targetHandleId = edge?.targetHandle || targetHandle;

    if (!sourceHandleId || !targetHandleId) {
      return;
    }

    // Extract handle names (last part after dash, e.g., "weather_1-T_ext" -> "T_ext")
    const sourceHandleName = sourceHandleId.includes('-') ? sourceHandleId.split('-').pop() : sourceHandleId;
    const targetHandleName = targetHandleId.includes('-') ? targetHandleId.split('-').pop() : targetHandleId;

    // Find handles by matching data-label or id within the correct node
    const findHandles = (nodeId, handleName) => {
      // Find the node first
      const nodes = document.querySelectorAll('.react-flow__node');
      const targetNode = Array.from(nodes).find(node => {
        const nodeDataId = node.getAttribute('data-id');
        const nodeIdAttr = node.getAttribute('id');
        return nodeDataId === nodeId || nodeIdAttr === nodeId || node.id === nodeId;
      });

      if (!targetNode) {
        return [];
      }

      // Find handles within this node
      const handlesInNode = targetNode.querySelectorAll('.react-flow__handle');
      const matches = Array.from(handlesInNode).filter(handle => {
        const handleId = handle.id || handle.getAttribute('id') || '';
        const handleLabel = handle.getAttribute('data-label') || '';
        
        // Match by exact handle name
        if (handleId === handleName || handleLabel === handleName) {
          return true;
        }
        
        // Match if handle ID ends with the handle name
        if (handleId.endsWith(`-${handleName}`) || handleId.includes(handleName)) {
          return true;
        }
        
        return false;
      });

      return matches;
    };

    const sourceHandles = findHandles(source, sourceHandleName);
    const targetHandles = findHandles(target, targetHandleName);
    const handlesToHighlight = [...new Set([...sourceHandles, ...targetHandles])];

    if (isActive) {
      // Add highlight class to handles
      handlesToHighlight.forEach(handle => {
        handle.classList.add('edge-highlighted-handle');
        // Ensure port class exists for badge styling
        if (!handle.classList.contains('port')) {
          handle.classList.add('port');
        }
        // Ensure data-label exists
        if (!handle.getAttribute('data-label') && handle.id) {
          handle.setAttribute('data-label', handle.id.split('-').pop() || handle.id);
        }
      });
    } else {
      // Remove highlight class from all handles
      document.querySelectorAll('.react-flow__handle.edge-highlighted-handle').forEach(handle => {
        handle.classList.remove('edge-highlighted-handle');
      });
    }

    // Cleanup
    return () => {
      if (!isActive) {
        handlesToHighlight.forEach(handle => {
          handle.classList.remove('edge-highlighted-handle');
        });
      }
    };
  }, [isActive, source, target, sourceHandle, targetHandle, id, edge]);

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          ...style,
          stroke: strokeColor,
          strokeWidth: style.strokeWidth || 3,
          strokeDasharray,
          strokeOpacity,
          pointerEvents: 'stroke',
        }}
        data-isbatchtomodel={data?.isBatchToModel ? 'true' : 'false'}
        data-source-handle={sourceHandle}
        data-target-handle={targetHandle}
        data-source-node={source}
        data-target-node={target}
      />
      {/* Transparent hit area with increased width for easier hovering */}
      <path
        d={edgePath}
        fill="none"
        stroke="transparent"
        strokeWidth={(style.strokeWidth || 3) + 8}
        pointerEvents="stroke"
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      />
    </>
  );
};
export default CustomEdge