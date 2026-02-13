export type Building = {
  id: string | number;
  height?: number;
  surface_area?: number;
  usage_category?: string;
  construction_period?: string;
  number_of_floors?: string;
  section_number?: string | number;
  net_leased_area?: number;
  total_floors?: number;
  net_leased_volume?: number;
  usage_type?: string;
  year?: number;
  number_of_people?: number;
  number_of_families?: number;
  building_type?: string;
  // original props passthrough optional
  __raw?: any;
};

const nf = (v: any): number | undefined => {
  if (v === '' || v == null || v === 'none' || v === 'None') return undefined;
  const s = String(v).replace(',', '.');
  const n = Number(s);
  return isNaN(n) ? undefined : n;
};

const ns = (v: any): string | undefined => {
  if (v === '' || v == null) return undefined;
  return String(v).trim();
};

const extractYear = (v: any): number | undefined => {
  if (!v) return undefined;
  const m = String(v).match(/\d{4}/);
  return m ? Number(m[0]) : undefined;
};

export function normalizeBuilding(raw: any): Building {
  // Support multiple key variants from our mock properties
  const p = raw || {};
  const get = (...keys: string[]) => keys.find(k => p[k] !== undefined) ? p[keys.find(k => p[k] !== undefined)!] : undefined;
  return {
    id: get('ID', 'id', 'Id', 'fid') ?? p.id,
    height: nf(get('Height', 'altezza_vo', 'height')),
    surface_area: nf(get('Surface Area', 'superficie', 'surface_area')),
    usage_category: ns(get('Usage Category', 'categ_uso', 'usage_category')),
    construction_period: ns(get('Construction Period', 'epoca_cost', 'construction_period')),
    number_of_floors: ns(get('Number of Floors', 'num_piani', 'number_of_floors')),
    section_number: get('Section Number', 'nsez', 'section_number'),
    net_leased_area: nf(get('Net Leased Area', 'net_leased_area')),
    total_floors: nf(get('Total Floors', 'number_of_floors', 'total_floors')),
    net_leased_volume: nf(get('Net Leased Volume', 'net_leased_volume')),
    usage_type: ns(get('Usage Type', 'usage', 'usage_type')),
    year: extractYear(get('Year', 'year')),
    number_of_people: nf(get('Number of People', 'n_people')),
    number_of_families: nf(get('Number of Families', 'n_families')),
    building_type: ns(get('Building Type', 'tab_type', 'building_type')),
    __raw: p,
  };
}














