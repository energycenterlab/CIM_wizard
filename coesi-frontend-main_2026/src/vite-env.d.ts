/// <reference types="vite/client" />
/// <reference types="react" />

declare module '@mapbox/mapbox-gl-draw' {
  export default class MapboxDraw {
    constructor(options?: any);
    add(geojson: any): void;
    delete(ids: string[]): void;
    deleteAll(): void;
    get(featureId?: string): any;
    getAll(): any;
    onChange(callback: (features: any) => void): void;
    onAdd(map: any): HTMLElement;
    onRemove(map: any): void;
  }
}

declare module '../components/NodeDnD/DnDContext' {
  export const DnDProvider: React.ComponentType<any>;
  export function useDnDContext(): any;
}

declare module '../components/NodeDnD/DnDFlow' {
  const DnDFlow: React.ComponentType<any>;
  export default DnDFlow;
}

declare module '../components/NodeDnD/DnDFlowForScey' {
  const DnDFlowForSce: React.ComponentType<any>;
  export default DnDFlowForSce;
}

declare module '../../components/NodeDnD/DnDContext' {
  export const DnDProvider: React.ComponentType<any>;
  export function useDnDContext(): any;
}

declare module '../../components/NodeDnD/DnDFlow' {
  const DnDFlow: React.ComponentType<any>;
  export default DnDFlow;
}

declare module '../../components/NodeDnD/DnDFlowForScey' {
  const DnDFlowForSce: React.ComponentType<any>;
  export default DnDFlowForSce;
}

interface Window {
  reactFlowState?: {
    nodes?: any[];
    edges?: any[];
  };
}
