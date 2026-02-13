import React from 'react';
import { createPortal } from 'react-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../../main';
import { useBuildingsData } from '../../lib/buildings/useBuildingsData';

export default function ReviewDataModalPortal() {
  const assignments = useSelector((s: RootState) => s.assignments.assignments);
  const { features, isLoading } = useBuildingsData();
  const [open, setOpen] = React.useState(false);
  const [assignmentId, setAssignmentId] = React.useState<string | null>(null);
  const assignment = React.useMemo(() => assignments.find(a => String(a.id) === String(assignmentId)), [assignments, assignmentId]);

  React.useEffect(() => {
    const onOpen = (e: any) => {
      setAssignmentId(String(e?.detail?.assignmentId));
      setOpen(true);
    };
    const onClose = () => setOpen(false);
    window.addEventListener('review-data:open', onOpen as any);
    window.addEventListener('review-data:close', onClose as any);
    return () => {
      window.removeEventListener('review-data:open', onOpen as any);
      window.removeEventListener('review-data:close', onClose as any);
    };
  }, []);

  const rows = React.useMemo(() => {
    if (!assignment) return [] as any[];
    const idSet = new Set((assignment?.ids || []).map(String));
    return (features || [])
      .filter((f) => idSet.has(String(f.id)))
      .map((f) => ({
        ID: String(f.id),
        Height: typeof f.height === 'number' ? f.height : undefined,
        Year: typeof f.year === 'number' ? f.year : undefined,
        Usage: (f.usage_category || f.usage_type || '') + '',
        Type: (f.building_type || '') + '',
        Surface: typeof f.surface_area === 'number' ? f.surface_area : undefined,
      }));
  }, [features, assignment]);

  const mean = (arr: (number|undefined)[]) => {
    const nums = arr.filter((v): v is number => typeof v === 'number' && !Number.isNaN(v));
    if (!nums.length) return null;
    return nums.reduce((a,b)=>a+b,0)/nums.length;
  };

  const analytics = React.useMemo(() => ({
    meanHeight: mean(rows.map(r=>r.Height)),
    avgYear: mean(rows.map(r=>r.Year)),
    meanSurface: mean(rows.map(r=>r.Surface)),
    usageDist: (()=>{
      const total = rows.length || 1;
      const counts: Record<string, number> = {};
      rows.forEach(r => { const k = r.Usage || 'unknown'; counts[k] = (counts[k]||0)+1; });
      return Object.entries(counts).sort((a,b)=>b[1]-a[1]).map(([k,c])=>({k, pct: Math.round((c*10000)/total)/100}));
    })()
  }), [rows]);

  if (!open || !assignment) return null;

  return createPortal(
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 99999 }} onClick={() => setOpen(false)}>
      <div style={{ background: 'white', width: 900, maxWidth: '92vw', maxHeight: '85vh', minHeight: 480, borderRadius: 12, overflow: 'hidden', display: 'flex', flexDirection: 'column', boxShadow: '0 10px 30px rgba(0,0,0,0.25)', opacity: 1, transform: 'translateY(0)', transition: 'opacity 150ms ease, transform 150ms ease' }} onClick={(e) => e.stopPropagation()}>
        <div style={{ padding: 16, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontWeight: 700 }}>Review Data — {assignment.name}</div>
          <button onClick={() => setOpen(false)} style={{ background: 'transparent', border: 'none', fontSize: 20, cursor: 'pointer' }}>×</button>
        </div>
        <div style={{ padding: 16, borderBottom: '1px solid #f0f0f0' }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Analytics Summary</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12 }}>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
              <div style={{ color: '#6b7280', fontSize: 12 }}>Entities</div>
              <div style={{ fontWeight: 700, fontSize: 18 }}>{rows.length || assignment.count || 0}</div>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
              <div style={{ color: '#6b7280', fontSize: 12 }}>Mean Height</div>
              <div style={{ fontWeight: 700 }}>{analytics.meanHeight ? analytics.meanHeight.toFixed(1)+' m' : '-'}</div>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
              <div style={{ color: '#6b7280', fontSize: 12 }}>Avg Year</div>
              <div style={{ fontWeight: 700 }}>{analytics.avgYear ? Math.round(analytics.avgYear) : '-'}</div>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: 12 }}>
              <div style={{ color: '#6b7280', fontSize: 12 }}>Mean Surface</div>
              <div style={{ fontWeight: 700 }}>{analytics.meanSurface ? analytics.meanSurface.toFixed(1)+' m²' : '-'}</div>
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 6 }}>Usage Distribution</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {analytics.usageDist.map(u => (
                <span key={u.k} style={{ background: '#eef2ff', color: '#1f2937', borderRadius: 999, padding: '4px 10px', fontSize: 12 }}>{u.k}: {u.pct}%</span>
              ))}
            </div>
          </div>
        </div>
        <div style={{ padding: 16, overflow: 'auto', minHeight: 240 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Data Preview</div>
          {isLoading ? (
            <div style={{ color: '#6b7280', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, height: 180 }}>Loading…</div>
          ) : rows.length > 0 ? (
            <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f9fafb' }}>
                    {["ID","Height","Year","Usage","Type"].map((k) => (
                      <th key={k} style={{ textAlign: 'left', padding: '8px 10px', borderBottom: '1px solid #e5e7eb', fontSize: 12, color: '#374151' }}>{k}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(0, 200).map((row, idx) => (
                    <tr key={idx}>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.ID}</td>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Height ?? ''}</td>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Year ?? ''}</td>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Usage}</td>
                      <td style={{ padding: '8px 10px', borderBottom: '1px solid #f3f4f6', fontSize: 12 }}>{row.Type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ color: '#6b7280' }}>No detailed rows available. This batch has {assignment.count ?? 0} entities.</div>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}


