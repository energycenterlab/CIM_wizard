import { create } from 'zustand';
import type { Building } from '../lib/buildings/normalizers';

export type AssignmentRule =
  | { kind: 'all' }
  | { kind: 'filter'; clauses: FilterClause[] }
  | { kind: 'mapSelection'; ids: (string | number)[] }
  | { kind: 'random'; percent: number; seed: number }
  | { kind: 'stratified'; attr: keyof Building; buckets: { value: string | number; percent: number }[]; seed: number }
  | { kind: 'splitTo'; sourceBatchId: string; percent: number; seed: number };

export type FilterClause = {
  attr: keyof Building;
  op: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'contains' | 'between';
  value?: string | number;
  values?: (string | number)[];
  range?: [number, number];
};

export type AssignmentBatch = {
  id: string;
  name: string;
  createdAt: number;
  size: number;
  ids: (string | number)[];
  rule: AssignmentRule;
  meta?: { color?: string; note?: string };
};

type AssignmentsState = {
  batches: AssignmentBatch[];
  previewIds: (string | number)[];
  setPreview: (ids: (string | number)[]) => void;
  addBatch: (b: AssignmentBatch) => void;
  deleteBatch: (id: string) => void;
  updateBatchName: (id: string, name: string) => void;
  ensureDefaultAllBatch: (features: Building[]) => void;
};

export const useAssignmentsStore = create<AssignmentsState>((set, get) => ({
  batches: [],
  previewIds: [],
  setPreview: (ids) => set({ previewIds: Array.from(new Set(ids)) }),
  addBatch: (b) => set({ batches: [b, ...get().batches] }),
  deleteBatch: (id) => set({ batches: get().batches.filter(x => x.id !== id) }),
  updateBatchName: (id, name) => set({ batches: get().batches.map(x => x.id === id ? { ...x, name } : x) }),
  ensureDefaultAllBatch: (features) => {
    const exists = get().batches.some(b => b.id === 'all-buildings');
    if (exists) return;
    const ids = features.map(f => f.id);
    set({ batches: [{ id: 'all-buildings', name: 'building', createdAt: Date.now(), size: ids.length, ids, rule: { kind: 'all' } }, ...get().batches ] });
  },
}));














