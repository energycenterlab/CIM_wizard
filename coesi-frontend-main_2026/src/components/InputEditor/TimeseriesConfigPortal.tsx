import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../../main';
import { updateNode } from '../../slices/rfGraphSlice';

type UnitDropdownProps = { value: string; onChange: (u: string) => void; unitQuery: string; setUnitQuery: (s: string) => void };
const UnitDropdown: React.FC<UnitDropdownProps> = ({ value, onChange, unitQuery, setUnitQuery }) => {
  const [openU, setOpenU] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ top: number; left: number; width: number }>({ top: 0, left: 0, width: 220 });

  const openDropdown = () => {
    setOpenU(true);
    requestAnimationFrame(() => {
      if (!inputRef.current) return;
      const r = inputRef.current.getBoundingClientRect();
      setPos({ top: Math.round(r.bottom + 4), left: Math.round(r.left), width: Math.max(220, Math.round(r.width)) });
    });
  };
  const filteredGroups = useMemo(() => {
    const q = (unitQuery || '').toLowerCase();
    return UNIT_CATALOG
      .map((g) => {
        const groupMatch = q && g.group.toLowerCase().includes(q);
        const units = groupMatch ? g.units : g.units.filter((u) => u.toLowerCase().includes(q));
        return { group: g.group, units };
      })
      .filter((g) => g.units.length > 0 || q === '');
  }, [unitQuery]);

  useEffect(() => {
    if (!openU) return;
    const onDocClick = (e: MouseEvent) => {
      const t = e.target as Node;
      if (dropdownRef.current && dropdownRef.current.contains(t)) return;
      if (inputRef.current && inputRef.current.contains(t)) return;
      setOpenU(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpenU(false);
    };
    const onScrollOrResize = () => {
      if (!inputRef.current) return;
      const r = inputRef.current.getBoundingClientRect();
      setPos({ top: Math.round(r.bottom + 4), left: Math.round(r.left), width: Math.max(220, Math.round(r.width)) });
    };
    document.addEventListener('click', onDocClick, true);
    document.addEventListener('keydown', onKey);
    window.addEventListener('scroll', onScrollOrResize, true);
    window.addEventListener('resize', onScrollOrResize);
    return () => {
      document.removeEventListener('click', onDocClick, true);
      document.removeEventListener('keydown', onKey);
      window.removeEventListener('scroll', onScrollOrResize, true);
      window.removeEventListener('resize', onScrollOrResize);
    };
  }, [openU]);

  return (
    <div style={{ position: 'relative' }}>
      <input
        ref={inputRef}
        value={value}
        placeholder="Choose unit…"
        onFocus={openDropdown}
        onClick={openDropdown}
        readOnly
        style={{ width: 110, padding: '4px 6px', fontSize: 12, cursor: 'pointer', background: '#fff', border: '1px solid #e5e7eb' }}
      />
      {openU && createPortal(
        <div
          ref={dropdownRef}
          style={{
            position: 'fixed', top: pos.top, left: pos.left, width: pos.width, maxHeight: 220, overflow: 'auto',
            border: '1px solid #e5e7eb', background: '#fff', zIndex: 30000, borderRadius: 6,
            boxShadow: '0 6px 24px rgba(0,0,0,0.08)'
          }}
        >
          <div style={{ padding: 6, position:'sticky', top:0, background:'#fff', borderBottom:'1px solid #f3f4f6', zIndex:1 }}>
            <input
              placeholder="Search units"
              value={unitQuery}
              onChange={(e) => setUnitQuery(e.target.value)}
              style={{ width: '100%', padding: '6px 8px', fontSize: 12, border: '1px solid #e5e7eb', borderRadius: 4 }}
            />
          </div>
          {filteredGroups.map((group) => (
            <div key={group.group}>
              <div style={{ padding: '4px 8px', fontSize: 11, color: '#6b7280' }}>{group.group}</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, padding: '4px 8px' }}>
                {group.units.map((u) => (
                  <button
                    key={u}
                    onClick={() => { onChange(u); setOpenU(false); }}
                    style={{ padding: '4px 6px', fontSize: 12, border: '1px solid #e5e7eb', background: '#fff', borderRadius: 6, cursor: 'pointer' }}
                  >
                    {u}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>,
        document.body
      )}
    </div>
  );
};

type ParsedCSV = { headers: string[]; rows: string[][] };

const UNIT_CATALOG: { group: string; units: string[] }[] = [
  { group: 'Temperature', units: ['°C', 'K', '°F'] },
  { group: 'Irradiance', units: ['W/m²', 'kW/m²'] },
  { group: 'Humidity', units: ['%'] },
  { group: 'Wind speed', units: ['m/s', 'km/h', 'mph', 'kn'] },
  { group: 'Wind direction', units: ['deg', 'rad'] },
  { group: 'Pressure', units: ['Pa', 'hPa', 'kPa', 'bar', 'atm', 'mmHg'] },
  { group: 'Precipitation', units: ['mm/step', 'mm/h', 'in/h'] },
  { group: 'Power', units: ['W', 'kW', 'MW'] },
  { group: 'Energy', units: ['Wh', 'kWh', 'MWh'] },
  { group: 'Illuminance', units: ['lux'] },
  { group: 'Voltage/Current', units: ['V', 'kV', 'A', 'kA'] },
  { group: 'Frequency', units: ['Hz', 'kHz'] },
  { group: 'Dimensionless', units: ['-', '%'] },
];

function guessDelimiter(sample: string): string {
  const first = sample.split(/\r?\n/).slice(0, 5);
  const cand = [',', ';', '\t'];
  let best: string = ','; let bestScore = -1;
  for (const d of cand) {
    const score = first.map(l => (l.match(new RegExp(d, 'g')) || []).length).reduce((a,b)=>a+b,0);
    if (score > bestScore) { bestScore = score; best = d; }
  }
  return best;
}

function parseCSV(text: string): ParsedCSV {
  const delim = guessDelimiter(text);
  const lines = text.replace(/\r/g,'').split('\n');
  const out: string[][] = [];
  const parseLine = (line: string): string[] => {
    const res: string[] = [];
    let cur = ''; let inQ = false;
    for (let i=0;i<line.length;i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQ && line[i+1] === '"') { cur += '"'; i++; }
        else inQ = !inQ;
      } else if (ch === delim && !inQ) { res.push(cur); cur=''; }
      else cur += ch;
    }
    res.push(cur);
    return res;
  };
  for (const l of lines) { if (l.trim() !== '') out.push(parseLine(l)); }
  // header detection: pick first row whose next row is mostly numeric/date-like
  let headerIdx = 0;
  const isNumOrDate = (s: string) => /^-?\d+(\.\d+)?$/.test(s.trim()) || !Number.isNaN(Date.parse(s));
  for (let i=0;i<Math.min(10,out.length-1);i++) {
    const next = out[i+1] || [];
    const ratio = next.filter(isNumOrDate).length / Math.max(1,next.length);
    if (ratio >= 0.5) { headerIdx = i; break; }
  }
  const headers = out[headerIdx] || [];
  const rows = out.slice(headerIdx+1);
  return { headers, rows };
}

type DetectedTime = { colIdx: number|null; confidence: number; startISO: string|null; stepSeconds: number|null };

function detectTimeAndStep(headers: string[], rows: string[][]): DetectedTime {
  const n = Math.min(rows.length, 5000);
  let bestCol: number|null = null; let bestScore = -1; let bestStart: string|null = null; let bestStep: number|null = null;
  for (let c=0;c<headers.length;c++) {
    const ts: number[] = [];
    for (let r=0;r<n;r++) {
      const v = rows[r]?.[c] || '';
      const t = Date.parse(v);
      if (!Number.isNaN(t)) ts.push(t);
    }
    const validRatio = ts.length / Math.max(1,n);
    if (validRatio < 0.5) continue;
    // monotonicity and step
    let inc = 0; const deltas: number[] = [];
    for (let i=1;i<ts.length;i++) { if (ts[i] > ts[i-1]) inc++; const d = Math.round((ts[i]-ts[i-1])/1000); if (d>0 && d<86400*7) deltas.push(d); }
    const mono = inc / Math.max(1, ts.length-1);
    const median = (arr: number[]) => { const s=[...arr].sort((a,b)=>a-b); const m=Math.floor(s.length/2); return s.length? (s.length%2?s[m]:(s[m-1]+s[m])/2):null; };
    const step = median(deltas) || null;
    const score = validRatio*0.7 + mono*0.3;
    if (score > bestScore) { bestScore = score; bestCol = c; bestStart = ts.length? new Date(ts[0]).toISOString(): null; bestStep = step; }
  }
  return { colIdx: bestCol, confidence: bestScore, startISO: bestStart, stepSeconds: bestStep };
}

function iqr(values: number[]) { const s=[...values].sort((a,b)=>a-b); const q1=s[Math.floor(s.length*0.25)]||0; const q3=s[Math.floor(s.length*0.75)]||0; return q3-q1; }

function detectNumericColumns(headers: string[], rows: string[][], timeCol: number|null) {
  const n = Math.min(rows.length, 5000);
  const sentinel = new Set(['', 'NaN', '-999','99','999','9999','99999','999999']);
  const cols: any[] = [];
  for (let c=0;c<headers.length;c++) {
    if (timeCol !== null && c === timeCol) continue;
    const nums: number[] = [];
    for (let r=0;r<n;r++) {
      let v = (rows[r]?.[c] || '').trim();
      if (sentinel.has(v)) continue;
      if (/^-?\d+,\d+$/.test(v)) v = v.replace(',','.');
      const f = parseFloat(v);
      if (!Number.isNaN(f)) nums.push(f);
    }
    const validRatio = nums.length / Math.max(1,n);
    if (validRatio < 0.6) continue;
    const variability = iqr(nums);
    if (variability < 1e-9) continue;
    // sample min/max
    const min = Math.min(...nums);
    const max = Math.max(...nums);
    cols.push({ colIdx: c, header: headers[c] || `col_${c}`, validRatio, variability, min, max, sample: nums.slice(0,5) });
  }
  return cols;
}

function suggestUnits(header: string, min: number, max: number): string[] {
  const h = header.toLowerCase();
  const chips: string[] = [];
  const add=(u:string)=>{ if(!chips.includes(u)) chips.push(u); };
  if (/(drybulb|temp|t_ext|_c|degc|°c)/.test(h)) add('°C');
  if (/(ghi|glohorzrad|dni|dhi|irr|w\/m2|w\s*\/\s*m2)/.test(h)) add('W/m²');
  if (/(relhum|rh|humidity|%)/.test(h)) add('%');
  if (/(windspd|ws)/.test(h)) add('m/s');
  if (/(winddir|wd|deg|dir)/.test(h)) add('deg');
  if (/(press|pa|hpa|kpa|atmos)/.test(h)) add('Pa');
  if (/(rain|precip)/.test(h)) add('mm/step');
  if (/(power|\bp\b|kw|mw)/.test(h)) add('W');
  if (/(energy|kwh|wh|mwh|\be\b)/.test(h)) add('Wh');
  if (/(lux|illum)/.test(h)) add('lux');
  // range hints
  if (min>-60 && max<140) add('°C');
  if (min>=0 && max<=100) add('%');
  if (max<=1500) add('W/m²');
  if (min>=0 && max<=60) add('m/s');
  if (max<=360) add('deg');
  if (min>=80000 && max<=110000) add('Pa');
  if (max<=20000) add('W');
  return chips.slice(0,5);
}

export default function TimeseriesConfigPortal() {
  const dispatch = useDispatch();
  const nodes = useSelector((s: RootState) => (s as any).rfGraph.nodes || []);
  const [open, setOpen] = useState(false);
  const [nodeId, setNodeId] = useState<string | null>(null);

  // UI State
  const [stage, setStage] = useState<'upload'|'time'|'ports'>('upload');
  const [modelName, setModelName] = useState('');
  const [parsed, setParsed] = useState<ParsedCSV|null>(null);
  const [timeCol, setTimeCol] = useState<number|null>(null);
  const [startISO, setStartISO] = useState<string>('');
  const [stepSec, setStepSec] = useState<number>(900);
  const [cols, setCols] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [unitQuery, setUnitQuery] = useState('');
  const [replaceMode, setReplaceMode] = useState(false);
  const [fileName, setFileName] = useState<string>('');
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    const handler = (e: any) => {
      const id = e.detail?.nodeId || null;
      setNodeId(id);
      setOpen(true);
      setReplaceMode(false);
      const node = nodes.find((n: any) => n.id === id);
      setModelName(node?.data?.name || node?.data?.label || '');
      const cfg = node?.data?.timeseriesConfig;
      if (cfg && Array.isArray(cfg.cols) && cfg.cols.length) {
        // Re-open in edit mode using stored config
        setParsed({ headers: cfg.cols.map((c:any)=>c.header), rows: [] });
        setTimeCol(cfg.timeCol ?? null);
        setStartISO(cfg.startISO || '');
        setStepSec(cfg.stepSec || 900);
        setCols(cfg.cols);
        setFileName(cfg.fileName || '');
        setStage('ports');
      } else {
        setStage('upload');
        setParsed(null);
        setCols([]);
        setFileName('');
      }
    };
    window.addEventListener('timeseries-config:open', handler as any);
    return () => window.removeEventListener('timeseries-config:open', handler as any);
  }, [nodes]);

  const close = () => setOpen(false);
  const node = nodes.find((n: any) => n.id === nodeId);

  // Build a merged view of all non-time columns when showAll is enabled
  const allColumnRows = useMemo(() => {
    if (!parsed) return [] as any[];
    const rows: any[] = [];
    const total = parsed.headers.length;
    for (let c = 0; c < total; c++) {
      if (timeCol !== null && c === timeCol) continue;
      const header = parsed.headers[c] || `col_${c}`;
      // baseline row for display when not detected as numeric
      rows.push({
        colIdx: c,
        header,
        validRatio: 0,
        variability: 0,
        min: undefined,
        max: undefined,
        sample: [],
        enabled: false,
        portName: header.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'') || `port_${c}`,
        unit: '',
        suggestions: suggestUnits(header, 0 as any, 0 as any),
        category: categorize(header),
        isExtra: true,
      });
    }
    return rows;
  }, [parsed, timeCol]);

  // Merge detected numeric cols with baseline rows when showAll
  const displayRows = useMemo(() => {
    if (!showAll) return cols;
    const map = new Map<number, any>();
    allColumnRows.forEach(r => map.set(r.colIdx, r));
    cols.forEach(r => map.set(r.colIdx, { ...map.get(r.colIdx), ...r, isExtra: false }));
    return Array.from(map.values());
  }, [showAll, cols, allColumnRows]);

  // Ensure hooks order is stable by declaring hook-using values before any early returns
  const filteredCols = useMemo(() => (displayRows).filter(c => c.header.toLowerCase().includes(search.toLowerCase()) || c.portName.toLowerCase().includes(search.toLowerCase())), [displayRows, search]);

  const canSave = useMemo(() => {
    if (timeCol===null) return false;
    const enabled = cols.filter(c=>c.enabled);
    if (enabled.length===0) return false;
    return enabled.every(c=>c.unit && c.unit.trim()!=='' && c.portName && c.portName.trim()!=='');
  }, [cols, timeCol]);

  if (!open || !nodeId) return null;

  const onFile = async (file: File) => {
    const text = await file.text();
    const p = parseCSV(text);
    setParsed(p);
    setFileName(file.name || 'uploaded.csv');
    // detect time
    const det = detectTimeAndStep(p.headers, p.rows);
    setTimeCol(det.colIdx);
    setStartISO(det.startISO || '');
    setStepSec(det.stepSeconds || 900);
    // detect numeric candidates
    const cands = detectNumericColumns(p.headers, p.rows, det.colIdx);
    // augment with UI fields
    const augmented = cands.map((c:any) => ({
      ...c,
      enabled: false,
      portName: c.header.toLowerCase().replace(/[^a-z0-9]+/g,'_').replace(/^_|_$/g,'') || `port_${c.colIdx}`,
      unit: '',
      suggestions: suggestUnits(c.header, c.min, c.max),
      category: categorize(c.header)
    }));
    setCols(augmented);
    setStage('time');
  };

  function categorize(h: string): string {
    const s=h.toLowerCase();
    if (/(temp|t_ext|drybulb|°c|degc)/.test(s)) return 'Thermal';
    if (/(irr|ghi|dni|dhi|w\/m2)/.test(s)) return 'Solar';
    if (/(wind)/.test(s)) return 'Wind';
    if (/(power|kw|mw)/.test(s)) return 'Power';
    if (/(press|pa|hpa|kpa|atmos)/.test(s)) return 'Pressure';
    if (/(hum|rh)/.test(s)) return 'Humidity';
    if (/(rain|precip)/.test(s)) return 'Precip';
    return 'Other';
  }

  const onSave = () => {
    if (!canSave) return;
    const enabled = cols.filter(c=>c.enabled);
    const output_variables = enabled.map((c:any) => ({
      name: c.portName,
      description: `From column ${c.header}`,
      unit: c.unit,
      start_value: '0',
      data_type: 'float',
      hidden: false,
      range: { min: 'none', max: 'none' },
      tags: [
        `source=${c.header}`,
        `unit_candidates=${c.suggestions.join('|')}`,
        `valid_ratio=${Math.round(c.validRatio*100)/100}`,
      ]
    }));
    const outputs = output_variables.map((v:any)=>v.name);
    const simulation_parameters = [
      { name: 'datafile', description: 'Uploaded CSV filename', unit: '', start_value: { value: 'uploaded.csv' } as any, data_type: 'string', hidden:false, range:{min:'none',max:'none'}, tags:[] },
      { name: 'start_date', description: 'Start date', unit: '', start_value: { value: startISO } as any, data_type: 'string', hidden:false, range:{min:'none',max:'none'}, tags:[] },
      { name: 'stepsize', description: 'Step size (s)', unit: 's', start_value: { value: String(stepSec) } as any, data_type: 'int', hidden:false, range:{min:'none',max:'none'}, tags:[] },
    ];

    const updates = {
      id: nodeId,
      type: node?.type,
      position: node?.position,
      data: {
        ...node?.data,
        name: modelName || node?.data?.name,
        simulation_parameters,
        output_variables,
        outputs,
        timeseriesConfig: {
          fileName,
          timeCol,
          startISO,
          stepSec,
          cols,
        }
      }
    } as any;
    dispatch(updateNode({ id: nodeId, updates }));
    // Force runtime RF update + redraw handles, and keep RF node data in sync (name, config, simulation params)
    window.dispatchEvent(new CustomEvent('rf:update-node', { detail: { 
      id: nodeId, 
      name: updates.data?.name,
      outputs, 
      output_variables,
      timeseriesConfig: updates.data?.timeseriesConfig,
      simulation_parameters: updates.data?.simulation_parameters,
    } }));
    setOpen(false);
  };

  const pickUnit = (c:any, u:string) => {
    setCols(prev => prev.map(x => x.colIdx===c.colIdx ? { ...x, unit: u } : x));
  };

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', zIndex: 20000 }} onClick={close}>
      <div onClick={(e) => e.stopPropagation()} style={{
        position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        background: '#fff', borderRadius: 12, width: 720, maxWidth: '90vw', maxHeight: 'calc(100vh - 48px)',
        overflow: 'hidden', boxShadow: '0 10px 30px rgba(0,0,0,0.25)', display:'flex', flexDirection:'column'
      }}>
        <div style={{ padding: 20, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontWeight: 700 }}>Timeseries configuration</div>
          <button onClick={close} title="Close" style={{ background: 'transparent', border: 'none', fontSize: 18, cursor: 'pointer', color:'#fca5a5' }}>×</button>
        </div>

        <div style={{ padding: 16, borderBottom:'1px solid #f3f4f6', display:'flex', gap:6, alignItems:'center' }}>
          <div style={{ color:'#6b7280', fontSize:12 }}>Model name</div>
          <input value={modelName} onChange={(e)=>setModelName(e.target.value)} style={{ padding:'6px 8px', border:'1px solid #e5e7eb', borderRadius:6, minWidth:160, width: 200 }} />
          {parsed && !replaceMode && (
            <div style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:8 }}>
              {fileName && <div style={{ fontSize:12, color:'#374151' }}>CSV: <strong>{fileName}</strong></div>}
              <button onClick={()=>{ setReplaceMode(true); setStage('upload'); }} style={{ border:'1px solid #e5e7eb', background:'#fff', borderRadius:6, padding:'6px 10px', fontSize:12, cursor:'pointer' }}>Replace file…</button>
              <button onClick={()=>{
                const overlay = document.createElement('div');
                overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:100000;';
                const box = document.createElement('div');
                box.style.cssText = 'pointer-events:auto;backdrop-filter:saturate(120%) blur(4px);background:rgba(255,255,255,0.95);border:1px solid rgba(0,0,0,0.08);border-radius:16px;box-shadow:0 8px 24px rgba(0,0,0,0.12);padding:20px;max-width:420px;width:90%';
                box.innerHTML = `<div style="font-weight:700;font-size:16px;color:#111827;margin-bottom:12px;">Remove CSV</div>
                <div style="font-size:13px;color:#374151;line-height:1.5;margin-bottom:20px;">Removing the CSV will clear selected ports and units. You will need to upload a new CSV and reconfigure. Continue?</div>
                <div style="display:flex;gap:8;justify-content:flex-end;">
                  <button id="ts-cancel" style="border:1px solid #E5E7EB;background:white;color:#111827;border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer;">Cancel</button>
                  <button id="ts-confirm" style="border:1px solid #DC2626;background:#DC2626;color:white;border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer;">Remove</button>
                </div>`;
                overlay.appendChild(box);
                document.body.appendChild(overlay);
                const cleanup = () => { document.body.removeChild(overlay); };
                (box.querySelector('#ts-cancel') as HTMLButtonElement).onclick = cleanup;
                (box.querySelector('#ts-confirm') as HTMLButtonElement).onclick = () => {
                  cleanup();
                  setParsed(null); setCols([]); setTimeCol(null); setStartISO(''); setStepSec(900); setFileName(''); setStage('upload');
                };
              }} style={{ border:'1px solid #ef4444', color:'#ef4444', background:'#fff', borderRadius:6, padding:'6px 10px', fontSize:12, cursor:'pointer' }}>Remove CSV</button>
            </div>
          )}
        </div>

        {stage==='upload' && (
          <div style={{ padding: 16 }}>
            <div style={{ marginBottom: 10, color:'#6b7280' }}>Upload or drag a CSV file</div>
            <div
              onClick={() => (document.getElementById('ts-csv') as HTMLInputElement | null)?.click()}
              onDragOver={(e)=>{ e.preventDefault(); }}
              onDrop={(e)=>{
                e.preventDefault();
                const dt = e.dataTransfer;
                let file = dt?.files && dt.files.length ? dt.files[0] : undefined;
                if (!file && dt?.items && dt.items.length) {
                  const item = dt.items[0];
                  if (item.kind === 'file') file = item.getAsFile() || undefined;
                }
                if (file) onFile(file);
              }}
              style={{ display:'block', padding: '30px', border:'2px dashed #94a3b8', borderRadius: 8, textAlign:'center', cursor:'pointer', color:'#475569' }}
              title="Drop CSV here or click to choose"
            >
              Drop CSV here or click to choose
              <input id="ts-csv" type="file" accept=".csv,text/csv" style={{ display:'none' }} onChange={(e)=>{ const f=e.target.files?.[0]; if (f) onFile(f); }} />
            </div>
          </div>
        )}

        {stage==='time' && parsed && (
          <div style={{ padding: 16, display:'grid', gridTemplateColumns:'1fr 1fr', gap:16, flex:1, minHeight:0, overflowY:'auto' }}>
            <div>
              <div style={{ fontWeight:600, marginBottom:8 }}>Time column</div>
              <select value={timeCol ?? ''} onChange={(e)=>setTimeCol(e.target.value===''?null:Number(e.target.value))} style={{ padding:'6px 8px', border:'1px solid #e5e7eb', borderRadius:6, minWidth:220 }}>
                <option value="">Select time column…</option>
                {parsed.headers.map((h,idx)=>(<option key={idx} value={idx}>{h||`col_${idx}`}</option>))}
              </select>
              {timeCol===null && (<div style={{ marginTop:8, color:'#b91c1c', fontSize:12 }}>No clear time column; please choose one.</div>)}
            </div>
            <div>
              <div style={{ fontWeight:600, marginBottom:8 }}>Start date (ISO)</div>
              <input value={startISO} onChange={(e)=>setStartISO(e.target.value)} placeholder="YYYY-MM-DDTHH:mm:ssZ" style={{ padding:'6px 8px', border:'1px solid #e5e7eb', borderRadius:6, minWidth:260 }} />
            </div>
            <div>
              <div style={{ fontWeight:600, marginBottom:8 }}>Step size (seconds)</div>
              <input type="number" value={stepSec} onChange={(e)=>setStepSec(Number(e.target.value)||0)} style={{ padding:'6px 8px', border:'1px solid #e5e7eb', borderRadius:6, minWidth:180 }} />
            </div>
            <div style={{ display:'flex', alignItems:'end', justifyContent:'flex-end' }}>
              <button onClick={()=>setStage('ports')} style={{ border:'1px solid #e5e7eb', background:'#111827', color:'#fff', borderRadius:8, padding:'8px 14px', fontSize:12, cursor:'pointer' }}>Next</button>
            </div>
          </div>
        )}

        {stage==='ports' && parsed && (
          <div style={{ padding: 16, display:'flex', flexDirection:'column', gap:12, flex:1, minHeight:0, overflowY:'auto' }}>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:12 }}>
              <input placeholder="Search columns/ports…" value={search} onChange={(e)=>setSearch(e.target.value)} style={{ flex:1, padding:'6px 8px', border:'1px solid #e5e7eb', borderRadius:6, minWidth:280, maxWidth:'520px' }} />
              <button
                aria-pressed={showAll}
                onClick={()=>setShowAll(v=>!v)}
                title="Show all columns"
                style={{
                  display:'inline-flex', alignItems:'center', gap:10,
                  background:'#f3f4f6', color:'#111827', border:'1px solid #d1d5db',
                  borderRadius:999, padding:'6px 12px', cursor:'pointer',
                  outline:'none', boxShadow:'none', WebkitTapHighlightColor:'transparent'
                }}
              >
                <span style={{ fontSize:12, fontWeight:600 }}>Show all</span>
                <span style={{ position:'relative', width:34, height:18, background:'#ffffff', border:'1px solid #d1d5db', borderRadius:999 }}>
                  <span style={{ position:'absolute', top:'50%', transform:'translateY(-50%)', left: showAll ? 15 : 3, width:16, height:16, borderRadius:'50%', background: showAll ? '#000000' : '#6b7280', boxShadow:'0 0 0 1px rgba(0,0,0,0.05)', transition:'left 160ms ease, background-color 160ms ease, transform 120ms ease' }} />
                </span>
              </button>
            </div>
            <div style={{ border:'1px solid #e5e7eb', borderRadius:8, overflow:'visible' }}>
              <div style={{ maxHeight: 360, overflowY:'auto', overflowX:'visible' }}>
                <table style={{ width:'100%', borderCollapse:'collapse' }}>
                  <thead style={{ position:'sticky', top:0, background:'#f9fafb', zIndex:1 }}>
                    <tr>
                      <th style={{ textAlign:'left', padding:'8px 8px', fontSize:12, width:'18%' }}>Port Name</th>
                      <th style={{ textAlign:'left', padding:'8px 8px', fontSize:12, width:'30%' }}>From column</th>
                      <th style={{ textAlign:'left', padding:'8px 8px', fontSize:12, width:'52%' }}>Unit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCols.map((c:any, rowIdx:number) => (
                      <tr key={c.colIdx} style={{ background: c.enabled ? '#eef6ff' : (rowIdx % 2 === 1 ? '#fafafa' : 'transparent'), borderBottom: '1px solid #f1f5f9' }}>
                        <td style={{ padding:'6px 8px' }}>
                          <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                            <input type="checkbox" checked={!!c.enabled} onChange={(e)=>setCols(prev=>{
                              const idx = prev.findIndex(x=>x.colIdx===c.colIdx);
                              if (idx>=0) return prev.map(x=>x.colIdx===c.colIdx?{...x,enabled:e.target.checked}:x);
                              // add extra row into state when toggled
                              return [...prev, { ...c, enabled: e.target.checked }];
                            })} />
                            <input value={c.portName} onChange={(e)=>setCols(prev=>{
                              const idx = prev.findIndex(x=>x.colIdx===c.colIdx);
                              if (idx>=0) return prev.map(x=>x.colIdx===c.colIdx?{...x,portName:e.target.value}:x);
                              return [...prev, { ...c, portName: e.target.value }];
                            })} style={{ width: 200, padding:'6px 8px', border:'1px solid #e5e7eb', borderRadius:6 }} />
                          </div>
                        </td>
                        <td style={{ padding:'6px 8px', fontSize:12 }} title={`e.g. ${c.sample.join(', ')}`}>{c.header}</td>
                        <td style={{ padding:'6px 8px' }}>
                          <div style={{ display:'flex', alignItems:'center', gap:6, flexWrap:'nowrap', overflowX:'auto' }}>
                            <UnitDropdown value={c.unit} onChange={(u)=>pickUnit(c,u)} unitQuery={unitQuery} setUnitQuery={setUnitQuery} />
                            <div style={{ display:'flex', gap:6, flexWrap:'nowrap', whiteSpace:'nowrap' }}>
                              {c.suggestions.map((u:string)=> (
                                <button key={u} onClick={()=>pickUnit(c,u)} style={{ padding:'2px 6px', fontSize:12, border:'1px solid #e5e7eb', background:'#fff', borderRadius:999, cursor:'pointer' }}>{u}</button>
                              ))}
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
        <div style={{ padding: 16, borderTop: '1px solid #eee', display:'flex', justifyContent:'flex-end', gap:8, background:'#fff' }}>
          <button onClick={close} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 6, padding: '8px 12px' }}>Cancel</button>
          <button disabled={!canSave} onClick={onSave} style={{ opacity: canSave?1:0.5, background: '#2563eb', color: 'white', border: 'none', borderRadius: 6, padding: '8px 12px' }}>Save</button>
        </div>
      </div>
    </div>
  );
}


