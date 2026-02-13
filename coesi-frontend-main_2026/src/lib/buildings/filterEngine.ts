import type { Building } from './normalizers';

export type FilterOp = 'eq'|'neq'|'gt'|'gte'|'lt'|'lte'|'in'|'contains'|'between';
export type Clause = { attr: keyof Building; op: FilterOp; value?: any; values?: any[]; range?: [number, number] };

// Simple deterministic LCG
export function rng(seed: number) {
  let s = (seed >>> 0) || 1;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 0x100000000;
  };
}

export function applyClauses(features: Building[], clauses: Clause[]): Building[] {
  return features.filter(f => clauses.every(c => matchClause(f, c)));
}

function matchClause(f: Building, c: Clause): boolean {
  const v: any = (f as any)[c.attr];
  switch (c.op) {
    case 'eq': return v === c.value;
    case 'neq': return v !== c.value;
    case 'gt': return typeof v === 'number' && typeof c.value === 'number' && v > c.value;
    case 'gte': return typeof v === 'number' && typeof c.value === 'number' && v >= c.value;
    case 'lt': return typeof v === 'number' && typeof c.value === 'number' && v < c.value;
    case 'lte': return typeof v === 'number' && typeof c.value === 'number' && v <= c.value;
    case 'between': {
      if (!c.range) return false;
      const [a, b] = c.range;
      return typeof v === 'number' && v >= Math.min(a, b) && v <= Math.max(a, b);
    }
    case 'in': return Array.isArray(c.values) && c.values.includes(v);
    case 'contains': return typeof v === 'string' && typeof c.value === 'string' && v.toLowerCase().includes(c.value.toLowerCase());
    default: return false;
  }
}

export function samplePercent(ids: (string|number)[], percent: number, seed: number): (string|number)[] {
  const take = Math.max(0, Math.min(ids.length, Math.round((percent / 100) * ids.length)));
  const r = rng(seed);
  // Shuffle deterministically then take first N
  const arr = ids.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(r() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr.slice(0, take);
}

export function stratifiedSample(features: Building[], attr: keyof Building, percent: number, seed: number): (string|number)[] {
  // Group by attr; for non-string numeric, coerce to string buckets
  const groups = new Map<string, Building[]>();
  for (const f of features) {
    const val = (f as any)[attr];
    const key = val == null ? '∅' : String(val);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(f);
  }
  let seedShift = seed;
  const out: (string|number)[] = [];
  for (const g of groups.values()) {
    const ids = g.map(x => x.id);
    const portion = samplePercent(ids, percent, ++seedShift);
    out.push(...portion);
  }
  return out;
}

export function samplePercentWeighted(ids: (string|number)[], percent: number, seed: number, weightBy: string, features: any[]): (string|number)[] {
  if (weightBy === 'uniform') {
    return samplePercent(ids, percent, seed);
  }
  
  const r = rng(seed);
  const count = Math.max(0, Math.min(ids.length, Math.round((percent / 100) * ids.length)));
  
  // Create feature map for quick lookup
  const featureMap = new Map();
  features.forEach(f => featureMap.set(f.id, f));
  
  // Calculate weights for each building
  const weightedIds = ids.map(id => {
    const feature = featureMap.get(id);
    if (!feature) return { id, weight: 1 };
    
    let weight = 1;
    switch (weightBy) {
      case 'surface_area':
        weight = feature.surface_area || 1;
        break;
      case 'height':
        weight = feature.height || 1;
        break;
      case 'year':
        weight = feature.year || 1;
        break;
      case 'total_floors':
        weight = feature.total_floors || 1;
        break;
      default:
        weight = 1;
    }
    
    // Ensure positive weights
    return { id, weight: Math.max(weight, 0.1) };
  });
  
  // Weighted random selection
  const totalWeight = weightedIds.reduce((sum, item) => sum + item.weight, 0);
  const selected = [];
  const remaining = [...weightedIds];
  let currentTotalWeight = totalWeight;
  
  for (let i = 0; i < count && remaining.length > 0; i++) {
    const random = r() * currentTotalWeight;
    let currentWeight = 0;
    
    for (let j = 0; j < remaining.length; j++) {
      currentWeight += remaining[j].weight;
      if (random <= currentWeight) {
        selected.push(remaining[j].id);
        currentTotalWeight -= remaining[j].weight;
        remaining.splice(j, 1);
        break;
      }
    }
  }
  
  return selected;
}












