import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../main';
import { normalizeBuilding, type Building } from './normalizers';

export function useBuildingsData(): { features: Building[]; isLoading: boolean; error?: string } {
  const scenarioLayers = useSelector((s: RootState) => s.scenarioLayers.layerGeojsonList);
  const [features, setFeatures] = useState<Building[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | undefined>(undefined);

  useEffect(() => {
    try {
      setIsLoading(true);
      const list = Array.isArray(scenarioLayers) ? scenarioLayers : [];
      const all: any[] = [];
      for (const g of list) {
        if (!g?.features) continue;
        for (const f of g.features) {
          // Ensure only buildings-like layers (by heuristic on properties)
          if (f?.properties && (f.properties.id !== undefined || f.properties.ID !== undefined)) {
            all.push(f.properties);
          }
        }
      }
      const norm = all.map(normalizeBuilding).filter(b => b.id !== undefined);
      setFeatures(norm);
      setIsLoading(false);
    } catch (e: any) {
      setError(e?.message || 'Failed to load buildings');
      setIsLoading(false);
    }
  }, [scenarioLayers]);

  return { features, isLoading, error };
}














