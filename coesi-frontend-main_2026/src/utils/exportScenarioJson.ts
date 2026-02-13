import { RootState } from '../main';

export interface ScenarioExportData {
  metadata: {
    exportDate: string;
    version: string;
    description: string;
  };
  // Complete workspace state
  nodes: any[];
  edges: any[];
  assignments: any[];
  compositeModels?: any[];
  modelDefinitions?: any[];
  // Scenario settings
  scenarioSettings: {
    startDate?: string;
    stopDate?: string;
    stepSize?: number;
    [key: string]: any;
  };
}

/**
 * Serializes the current node editor state to JSON format
 * This will be used by the YAML builder microservice
 * Captures the COMPLETE workspace state for reconstruction
 */
export function exportScenarioToJson(state: RootState): ScenarioExportData {
  const now = new Date();
  
  // We no longer send compositeModels/modelDefinitions; composites must be flattened into normal nodes/edges
  
  console.log(`📊 Optimized Export Summary:`);
  console.log(`   - Total nodes in workspace: ${(state.rfGraph.nodes || []).length}`);
  console.log(`   - Total edges in workspace: ${(state.rfGraph.edges || []).length}`);
  console.log(`   - Total assignments: ${(state.assignments.assignments || []).length}`);
  // Composite metadata intentionally omitted from export
  console.log(`   - 🚀 JSON size optimized: trimmed UI-only fields and duplicate ID lists removed`);
  
  const sanitizedNodes = (state.rfGraph.nodes || []).map((n: any) => {
    try {
      const { position, ...restNode } = n || {};
      const d = (restNode as any)?.data || {};
      const sims: string[] = Array.isArray(d.simulator_names) ? d.simulator_names : [];
      const selected = d.selected_simulator;
      const normalizedSelected = selected && typeof selected === 'string' && selected.trim() !== ''
        ? selected
        : (sims.length > 0 ? sims[0] : undefined);
      const { components, connections, possible_connections, ...dataRest } = d;
      const sanitizedData = normalizedSelected ? { ...dataRest, selected_simulator: normalizedSelected } : dataRest;
      return { ...restNode, data: sanitizedData };
    } catch {
      return n;
    }
  });

  // Flatten CompositeBlock nodes into normal nodes/edges for YAML_Builder
  const flatNodes: any[] = [];
  const flatEdges: any[] = [];
  const compositeIds = new Set<string>();
  const idMap: Record<string, string> = {}; // compositeId:innerId -> globalId

  const originalEdges = (state.rfGraph.edges || []).slice();

  sanitizedNodes.forEach((node: any) => {
    if ((node?.type || '') === 'CompositeBlock' && node?.data) {
      compositeIds.add(node.id);
      const compId = node.id;
      const compData = node.data || {};
      const innerNodes: any[] = Array.isArray(compData.nodes) ? compData.nodes : (Array.isArray(compData.originalComposite?.nodes) ? compData.originalComposite.nodes : []);
      const innerEdges: any[] = Array.isArray(compData.edges) ? compData.edges : (Array.isArray(compData.originalComposite?.edges) ? compData.originalComposite.edges : []);
      const bindGroups: string[][] = Array.isArray(compData.bindingGroupsNodeIds) ? compData.bindingGroupsNodeIds : [];
      const firstBindGroup: string[] = Array.isArray(bindGroups[0]) ? bindGroups[0] : [];

      // Materialize inner nodes as top-level nodes
      innerNodes.forEach((inNode: any) => {
        const globalId = `${compId}__${inNode.id}`;
        idMap[`${compId}:${inNode.id}`] = globalId;
        flatNodes.push({
          id: globalId,
          type: 'parameditor',
          data: inNode.data || { name: inNode.modelDefId || inNode.label || 'model' },
        });
      });

      // Helper: find inner node by attribute name
      const findInnerByAttr = (attr: string): string | null => {
        if (!attr) return null;
        for (const inNode of innerNodes) {
          const inputs: string[] = inNode.inputs || inNode.data?.inputs || [];
          const outputs: string[] = inNode.outputs || inNode.data?.outputs || [];
          if ((inputs && inputs.includes(attr)) || (outputs && outputs.includes(attr))) {
            return idMap[`${compId}:${inNode.id}`] || null;
          }
        }
        return null;
      };

      // Add inner edges
      innerEdges.forEach((ie: any, idx: number) => {
        const src = idMap[`${compId}:${ie.source}`];
        const tgt = idMap[`${compId}:${ie.target}`];
        if (src && tgt) {
          const srcAttr = (ie.sourceHandle && ie.sourceHandle.includes('-')) ? ie.sourceHandle.split('-').pop() : ie.sourceHandle;
          const tgtAttr = (ie.targetHandle && ie.targetHandle.includes('-')) ? ie.targetHandle.split('-').pop() : ie.targetHandle;
          flatEdges.push({
            id: `${compId}__ie_${idx}`,
            source: src,
            target: tgt,
            sourceHandle: srcAttr ? `${src.split('__').pop()}-${srcAttr}` : undefined,
            targetHandle: tgtAttr ? `${tgt.split('__').pop()}-${tgtAttr}` : undefined,
            type: 'custom',
            data: ie.data || {},
          });
        }
      });

      // Rewire external edges touching the composite node
      originalEdges.forEach((e: any) => {
        // assignment batch to composite → to all nodes in first bind group
        if (e.target === compId && e.data?.isBatchToModel) {
          firstBindGroup.forEach((innerId: string, i: number) => {
            const tgtGlobal = idMap[`${compId}:${innerId}`];
            if (tgtGlobal) {
              flatEdges.push({
                id: `${e.id}__flat_${i}`,
                source: e.source,
                target: tgtGlobal,
                sourceHandle: e.sourceHandle,
                targetHandle: `${innerId}-batch-target`,
                type: e.type || 'custom',
                data: { ...e.data },
              });
            }
          });
          return;
        }

        const parseAttr = (h: string) => (h && h.includes('-') ? h.split('-').pop() : h);
        if (e.target === compId) {
          const attr = parseAttr(e.targetHandle || '');
          const innerTarget = findInnerByAttr(attr || '');
          if (innerTarget) {
            const originalData = e.data || {};
            // Create new data object with default connectionType if needed (don't modify frozen object)
            let edgeData = { ...originalData };
            // Set default connectionType for regular model-to-model connections
            if (!edgeData.isBatchToModel && !edgeData.isModelToModelEntityConnection && !edgeData.connectionType) {
              edgeData = { ...edgeData, connectionType: 'Same Time' };
            }
            flatEdges.push({
              id: `${e.id}__flat_to`,
              source: e.source,
              target: innerTarget,
              sourceHandle: e.sourceHandle,
              targetHandle: attr ? `${innerTarget.split('__').pop()}-${attr}` : undefined,
              type: e.type || 'custom',
              data: edgeData,
            });
          }
        } else if (e.source === compId) {
          const attr = parseAttr(e.sourceHandle || '');
          const innerSource = findInnerByAttr(attr || '');
          if (innerSource) {
            const originalData = e.data || {};
            // Create new data object with default connectionType if needed (don't modify frozen object)
            let edgeData = { ...originalData };
            // Set default connectionType for regular model-to-model connections
            if (!edgeData.isBatchToModel && !edgeData.isModelToModelEntityConnection && !edgeData.connectionType) {
              edgeData = { ...edgeData, connectionType: 'Same Time' };
            }
            flatEdges.push({
              id: `${e.id}__flat_from`,
              source: innerSource,
              target: e.target,
              sourceHandle: attr ? `${innerSource.split('__').pop()}-${attr}` : undefined,
              targetHandle: e.targetHandle,
              type: e.type || 'custom',
              data: edgeData,
            });
          }
        }
      });
    } else {
      flatNodes.push(node);
    }
  });

  // Keep only edges that don't touch composite nodes; others were rewired above
  (state.rfGraph.edges || []).forEach((e: any) => {
    if (!compositeIds.has(e.source) && !compositeIds.has(e.target)) {
      // Preserve edge data including connectionType, with default "Same Time" for model-to-model connections
      const originalData = e.data || {};
      // Create new data object with default connectionType if needed (don't modify frozen object)
      let edgeData = { ...originalData };
      // Set default connectionType for regular model-to-model connections (not batch or entity connections)
      if (!edgeData.isBatchToModel && !edgeData.isModelToModelEntityConnection && !edgeData.connectionType) {
        edgeData = { ...edgeData, connectionType: 'Same Time' };
      }
      flatEdges.push({
        id: e.id,
        source: e.source,
        target: e.target,
        sourceHandle: e.sourceHandle,
        targetHandle: e.targetHandle,
        type: e.type || 'custom',
        data: edgeData,
      });
    }
  });

  const minimalAssignments = (state.assignments.assignments || [])
    .filter((a: any) => String(a?.entityType || '').toLowerCase() === 'building')
    .map((a: any) => ({ id: a.id, name: a.name, entityType: 'building', ids: Array.isArray(a.ids) ? a.ids : [] }));

  // Helpers to derive default parallel process count from graph topology
  const nodesById: Record<string, any> = {};
  flatNodes.forEach((n) => { nodesById[n.id] = n; });
  const looksEntity = (h: string) => typeof h === 'string' && (h.endsWith('-batch') || h.endsWith('-batch-source') || h.endsWith('-batch-target'));
  const isEntityEdge = (e: any) => {
    if (!e) return false;
    if (e.data?.isModelToModelEntityConnection) return true;
    return looksEntity(e.sourceHandle || '') && looksEntity(e.targetHandle || '');
  };
  const getAssignmentCountById = (assignmentId: string | number | undefined | null) => {
    if (!assignmentId && assignmentId !== 0) return null;
    const found = (state.assignments.assignments || []).find((a: any) => String(a.id) === String(assignmentId));
    if (!found) return null;
    const count = (found.count != null ? found.count : (Array.isArray(found.ids) ? found.ids.length : 0));
    return typeof count === 'number' ? count : null;
  };
  const directOrIncomingBatchCount = (nodeId: string): number | null => {
    const node = nodesById[nodeId];
    if (!node) return null;
    const direct = getAssignmentCountById(node?.data?.assignmentBatchId);
    if (direct != null) return direct;
    for (const e of flatEdges) {
      if (e?.target === nodeId && e?.data?.isBatchToModel && e?.source) {
        const srcNode = nodesById[e.source];
        const cnt = getAssignmentCountById(srcNode?.data?.assignmentBatchId);
        if (cnt != null) return cnt;
      }
    }
    return null;
  };
  const entityCountForNode = (startId: string): number | null => {
    // Step 1: direct or incoming batch
    const direct = directOrIncomingBatchCount(startId);
    if (direct != null) return direct;
    // Step 2: BFS over entity edges (pink connections)
    const visited = new Set<string>();
    const queue: string[] = [startId];
    visited.add(startId);
    while (queue.length > 0) {
      const cur = queue.shift() as string;
      // check direct/incoming for neighbor as well
      const c = directOrIncomingBatchCount(cur);
      if (c != null) return c;
      for (const e of flatEdges) {
        if (!isEntityEdge(e)) continue;
        let neighbor: string | null = null;
        if (e.source === cur) neighbor = e.target;
        else if (e.target === cur) neighbor = e.source;
        if (neighbor && !visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }
    return null;
  };

  // Scenario Settings: read from sessionStorage (scoped to current route) or compute defaults
  const formatDate = (d: Date) => {
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  };
  const normalizePathForStorage = (pathname: string) => {
    // The app is mounted with React Router basename="/urbansim" (see src/main.tsx),
    // but `window.location.pathname` includes the basename while `useLocation().pathname` does not.
    // Normalize so exportScenarioToJson reads the same sessionStorage key as ScenarioSettingBoard.
    if (!pathname) return '/';
    const stripped = pathname.replace(/^\/urbansim(\/|$)/, '/');
    return stripped || '/';
  };
  // Default dates aligned with UI requested defaults:
  // 01/01/2015 -> 2015-01-01, 31/01/2015 -> 2015-01-31
  let startDateStr = '2015-01-01';
  let endDateStr = '2015-01-31';
  let portSelectionMode: 'all' | 'output' | 'input' | 'modified' = 'all';
  let selectedPortsFromUI: string[] = [];
  try {
    // Use same storage key as ScenarioSettingBoard
    const rawPath = (typeof window !== 'undefined' && window.location?.pathname) || '';
    const path = normalizePathForStorage(rawPath);
    const storageKey = `output-config:${path}`;
    const raw = (typeof window !== 'undefined' && window.sessionStorage.getItem(storageKey)) || null;
    if (raw) {
      const parsed = JSON.parse(raw);
      if (typeof parsed?.startDate === 'string') startDateStr = parsed.startDate;
      if (typeof parsed?.endDate === 'string') endDateStr = parsed.endDate;
      // New: deterministic radio selection mode
      if (parsed?.portSelectionMode === 'all' || parsed?.portSelectionMode === 'output' || parsed?.portSelectionMode === 'input' || parsed?.portSelectionMode === 'modified') {
        portSelectionMode = parsed.portSelectionMode;
      } else if (typeof parsed?.allPortsChecked === 'boolean' && parsed.allPortsChecked === true) {
        // Back-compat: old versions used a checkbox. "All ports" checked means select all.
        portSelectionMode = 'all';
      }
      if (Array.isArray(parsed?.selectedPorts)) {
        selectedPortsFromUI = parsed.selectedPorts;
      }
    }
  } catch {
    // ignore storage errors
  }

  // Build available ports (inputs + outputs) across all workspace nodes.
  // IMPORTANT: CompositeBlock ports are *exposed* ports; later we map them to the flattened inner node IDs.
  const availablePorts: Array<{ fullId: string; type: 'input' | 'output' }> = [];
  (sanitizedNodes || []).forEach((node: any) => {
    const isCompositeBlock = (node?.type || '') === 'CompositeBlock';
    const compInputs = node?.data?.exposedPorts?.inputs ?? node?.data?.unusedInputs ?? node?.data?.allInputs ?? [];
    const compOutputs = node?.data?.exposedPorts?.outputs ?? node?.data?.unusedOutputs ?? node?.data?.allOutputs ?? [];
    const inputs = isCompositeBlock ? compInputs : (node?.data?.input_variables || node?.data?.inputs || []);
    const outputs = isCompositeBlock ? compOutputs : (node?.data?.output_variables || node?.data?.outputs || []);

    inputs.forEach((input: any) => {
      const portName = typeof input === 'string' ? input : (input?.name || input);
      const fullId = `${node.id}.${portName}`;
      availablePorts.push({ fullId, type: 'input' });
    });
    outputs.forEach((output: any) => {
      const portName = typeof output === 'string' ? output : (output?.name || output);
      const fullId = `${node.id}.${portName}`;
      availablePorts.push({ fullId, type: 'output' });
    });
  });

  const selectedWorkspacePortIds = (() => {
    const selectedSet = new Set<string>(selectedPortsFromUI || []);

    if (portSelectionMode === 'all') {
      return availablePorts.map(p => p.fullId);
    }

    if (portSelectionMode === 'output') {
      const chosen = availablePorts
        .filter(p => p.type === 'output' && selectedSet.has(p.fullId))
        .map(p => p.fullId);
      // Default: outputs all selected
      return chosen.length > 0 ? chosen : availablePorts.filter(p => p.type === 'output').map(p => p.fullId);
    }

    if (portSelectionMode === 'input') {
      const chosen = availablePorts
        .filter(p => p.type === 'input' && selectedSet.has(p.fullId))
        .map(p => p.fullId);
      // Default: inputs all selected
      return chosen.length > 0 ? chosen : availablePorts.filter(p => p.type === 'input').map(p => p.fullId);
    }

    // modified: user must select at least one; enforce a safe fallback if empty
    const chosen = availablePorts
      .filter(p => selectedSet.has(p.fullId))
      .map(p => p.fullId);
    if (chosen.length > 0) return chosen;
    return availablePorts.length > 0 ? [availablePorts[0].fullId] : [];
  })();

  return {
    metadata: {
      exportDate: now.toISOString(),
      version: '1.0.0',
      description: 'Optimized scenario export for YAML Builder (trimmed UI-only fields)'
    },
    nodes: flatNodes.map((n: any) => {
      try {
        const dataObj = n?.data || {};
        const savedPc = dataObj?.computation_setting?.process_count;
        const tagsRaw = (dataObj?.tags ?? []);
        const tags = Array.isArray(tagsRaw) ? tagsRaw : [tagsRaw];
        const tagStrings = tags.map((t: any) => String(t).toLowerCase());
        const hasEntityPort = !tagStrings.includes('timeseries') && !tagStrings.includes('scheduler');
        let parallelVal: number | undefined = undefined;
        if (typeof savedPc === 'number') {
          parallelVal = savedPc;
        } else if (hasEntityPort) {
          const derived = entityCountForNode(n.id);
          if (typeof derived === 'number' && derived > 0) {
            parallelVal = derived;
          }
        }
        // Remove computation_setting from exported data to avoid duplication/contradiction
        const { computation_setting, ...restData } = dataObj;
        const finalData = typeof parallelVal === 'number'
          ? { ...restData, numberOfParallelProcesses: parallelVal }
          : restData;
        return { ...n, data: finalData };
      } catch {
        return n;
      }
    }),
    edges: flatEdges,
    assignments: minimalAssignments,
    // Scenario settings
    scenarioSettings: {
      startDate: `${startDateStr} 00:00:00`,
      stopDate: `${endDateStr} 00:00:00`,
      stepSize: 600,
      // Map workspace port IDs to the flattened graph IDs (CompositeBlock ports -> inner nodes).
      outputPorts: (() => {
        const parsePort = (fullId: string): { nodeId: string; portName: string } | null => {
          const idx = fullId.indexOf('.');
          if (idx === -1) return null;
          return { nodeId: fullId.slice(0, idx), portName: fullId.slice(idx + 1) };
        };

        const portTypeById: Record<string, 'input' | 'output'> = {};
        availablePorts.forEach((p) => { portTypeById[p.fullId] = p.type; });

        // Build per-composite attribute maps based on the original inner nodes
        const compositeAttrMaps: Record<string, { inputs: Record<string, string>; outputs: Record<string, string> }> = {};
        (sanitizedNodes || []).forEach((node: any) => {
          if ((node?.type || '') !== 'CompositeBlock') return;
          const compId = node.id;
          const compData = node.data || {};
          const innerNodes: any[] = Array.isArray(compData.nodes) ? compData.nodes : (Array.isArray(compData.originalComposite?.nodes) ? compData.originalComposite.nodes : []);
          const inputsMap: Record<string, string> = {};
          const outputsMap: Record<string, string> = {};
          innerNodes.forEach((inNode: any) => {
            const globalId = `${compId}__${inNode.id}`;
            const ins: any[] = (inNode?.inputs || inNode?.data?.inputs || []) as any[];
            const outs: any[] = (inNode?.outputs || inNode?.data?.outputs || []) as any[];
            ins.forEach((a: any) => {
              const attr = String(a);
              if (!inputsMap[attr]) inputsMap[attr] = globalId;
            });
            outs.forEach((a: any) => {
              const attr = String(a);
              if (!outputsMap[attr]) outputsMap[attr] = globalId;
            });
          });
          compositeAttrMaps[compId] = { inputs: inputsMap, outputs: outputsMap };
        });

        const result = new Set<string>();
        for (const wid of selectedWorkspacePortIds) {
          const parsed = parsePort(wid);
          if (!parsed) continue;
          const { nodeId, portName } = parsed;
          if (compositeIds.has(nodeId)) {
            const maps = compositeAttrMaps[nodeId];
            const pType = portTypeById[wid];
            const mappedNodeId =
              (pType === 'input' ? maps?.inputs?.[portName] : maps?.outputs?.[portName]) ||
              maps?.outputs?.[portName] ||
              maps?.inputs?.[portName];
            if (mappedNodeId) {
              result.add(`${mappedNodeId}.${portName}`);
            }
          } else {
            result.add(wid);
          }
        }
        return Array.from(result);
      })()
    }
  };
}

/**
 * Downloads the scenario data as a JSON file
 */
export function downloadScenarioJson(data: ScenarioExportData, filename?: string): void {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || `scenario-export-${new Date().toISOString().split('T')[0]}.json`;
  
  // Trigger download
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // Clean up
  URL.revokeObjectURL(url);
}
