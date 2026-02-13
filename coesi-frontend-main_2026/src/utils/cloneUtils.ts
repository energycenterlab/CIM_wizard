/**
 * Deep clone utility for ReactFlow nodes and edges
 * Uses structuredClone when available, falls back to JSON clone for compatibility
 */

/**
 * Deep clone an object using the most appropriate method available
 * @param obj - Object to clone
 * @returns Deep cloned object
 */
export function deepClone<T>(obj: T): T {
  // Use structuredClone if available (modern browsers)
  if (typeof structuredClone !== 'undefined') {
    try {
      return structuredClone(obj);
    } catch (error) {
      console.warn('structuredClone failed, falling back to JSON clone:', error);
    }
  }
  
  // Fallback to JSON clone for compatibility
  try {
    return JSON.parse(JSON.stringify(obj));
  } catch (error) {
    console.error('Deep clone failed:', error);
    throw new Error('Unable to clone object - contains non-serializable data');
  }
}

/**
 * Clone ReactFlow nodes array, ensuring all objects are mutable
 * @param nodes - Array of ReactFlow nodes
 * @returns Cloned array of nodes
 */
export function cloneNodes(nodes: any[]): any[] {
  if (!Array.isArray(nodes)) {
    return [];
  }
  
  return nodes.map(node => {
    const cloned = deepClone(node);
    
    // Ensure data object is properly cloned
    if (cloned.data && typeof cloned.data === 'object') {
      cloned.data = deepClone(cloned.data);
    }
    
    return cloned;
  });
}

/**
 * Clone ReactFlow edges array, ensuring all objects are mutable
 * @param edges - Array of ReactFlow edges
 * @returns Cloned array of edges
 */
export function cloneEdges(edges: any[]): any[] {
  if (!Array.isArray(edges)) {
    return [];
  }
  
  return edges.map(edge => {
    const cloned = deepClone(edge);
    
    // Ensure data and style objects are properly cloned
    if (cloned.data && typeof cloned.data === 'object') {
      cloned.data = deepClone(cloned.data);
    }
    
    if (cloned.style && typeof cloned.style === 'object') {
      cloned.style = deepClone(cloned.style);
    }
    
    if (cloned.markerEnd && typeof cloned.markerEnd === 'object') {
      cloned.markerEnd = deepClone(cloned.markerEnd);
    }
    
    return cloned;
  });
}

/**
 * Check if an object is frozen (read-only)
 * @param obj - Object to check
 * @returns True if object is frozen
 */
export function isFrozen(obj: any): boolean {
  if (obj === null || typeof obj !== 'object') {
    return false;
  }
  
  try {
    // Try to modify a property - if it fails, the object is likely frozen
    const testProp = '__freeze_test__';
    obj[testProp] = 'test';
    delete obj[testProp];
    return false;
  } catch {
    return true;
  }
}

/**
 * Development warning for frozen objects
 * @param obj - Object to check
 * @param context - Context for the warning message
 */
export function warnIfFrozen(obj: any, context: string): void {
  if (process.env.NODE_ENV === 'development' && isFrozen(obj)) {
    console.warn(`⚠️ Frozen object detected in ${context}. This may cause ReactFlow mutations to fail.`);
  }
}





