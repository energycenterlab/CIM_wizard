import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { coesiModelService } from '../services/coesiModels';

export default function ModelDetails() {
  const { userId, modelName } = useParams();
  const navigate = useNavigate();
  const [model, setModel] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModel = async () => {
      try {
        setLoading(true);
        setError(null);
        const coesiModel = await coesiModelService.getModel(String(modelName));
        if (coesiModel) {
          const convertedModel = coesiModelService.convertToModelJson(coesiModel);
          setModel(convertedModel);
        } else {
          setError('Model not found');
        }
      } catch (err) {
        console.error('Failed to fetch model:', err);
        setError('Failed to load model details from backend');
      } finally {
        setLoading(false);
      }
    };

    if (modelName) {
      fetchModel();
    }
  }, [modelName]);

  if (loading) {
    return (
      <div style={{ padding: 24 }}>
        <div>Loading model information...</div>
        <button onClick={() => navigate(`/projects/${userId}`)} style={{ padding: '6px 10px', border: '1px solid #ddd', background: '#fff', borderRadius: 6, marginTop: 12 }}>Back</button>
      </div>
    );
  }

  if (error || !model) {
    return (
      <div style={{ padding: 24 }}>
        <h2>Model not found</h2>
        <div style={{ color: '#dc2626', marginBottom: 12 }}>{error}</div>
        <button onClick={() => navigate(`/projects/${userId}`)}>Back</button>
      </div>
    );
  }

  const goBack = () => navigate(`/projects/${userId}`);

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ margin: 0 }}>{model.name}</h2>
        <button onClick={goBack} style={{ padding: '6px 10px', border: '1px solid #ddd', background: '#fff', borderRadius: 6 }}>Back</button>
      </div>
      <div style={{ color: '#666', marginTop: 6 }}>Description</div>
      <div style={{ marginBottom: 8 }}>{model.description}</div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 12 }}>
        {model.tags?.map((t: string) => (
          <span key={t} style={{ background: '#f1f5f9', color: '#334155', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>{t}</span>
        ))}
        <span style={{ background: '#DCFCE7', color: '#166534', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>COESI</span>
      </div>

      <div style={{ marginTop: 12 }}>
        <strong>Solver</strong>
        <div style={{ color: '#444' }}>{model.solver ?? '-'}</div>
      </div>
      <div style={{ marginTop: 12 }}>
        <strong>Execution Command</strong>
        <div style={{ color: '#444' }}>{model.model_execution_cmd ?? '-'}</div>
      </div>

      <SectionTable title="Simulation Parameters" headers={[ 'Name','Value','Unit','Type','Description' ]} rows={(model.simulation_parameters||[]).map((p: any) => [p.name, valueOf(p,'value'), p.unit||'', p.data_type, p.description||'' ])} />
      <SectionTable title="Output Variables" headers={[ 'Name','Description','Unit','Type','Start Value' ]} rows={(model.output_variables||[]).map((p: any) => [p.name, p.description||'', p.unit||'', p.data_type, valueOf(p,'start_value') ])} />
      <SectionTable title="Input Variables" headers={[ 'Name','Description','Unit','Type','Start Value' ]} rows={(model.input_variables||[]).map((p: any) => [p.name, p.description||'', p.unit||'', p.data_type, valueOf(p,'start_value') ])} />
      <SectionTable title="Model Parameters" headers={[ 'Name','Default Value','Unit','Type','Description','Range' ]} rows={(model.model_parameters||[]).map((p: any) => [p.name, valueOf(p,'default_value'), p.unit||'', p.data_type, p.description||'', rangeOf(p) ])} />

      {model.simulator_names?.length ? (
        <div style={{ marginTop: 16 }}>
          <strong>Available Simulators</strong>
          <ul>
            {model.simulator_names.map((s: string) => <li key={s}>{s}</li>)}
          </ul>
        </div>
      ) : null}

      {model.possible_connections?.length ? (
        <div style={{ marginTop: 16 }}>
          <strong>Possible Connections</strong>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
            {model.possible_connections.map((connection: string) => (
              <span key={connection} style={{ background: '#EFF6FF', color: '#1E40AF', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>
                {connection}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {/* Components (for composite models) */}
      {model.components?.length ? (
        <div style={{ marginTop: 16 }}>
          <strong>Components</strong>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
            {model.components.map((component: string) => (
              <span key={component} style={{ background: '#F0FDF4', color: '#166534', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>
                {component}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {/* Connections (for composite models) */}
      {model.connections?.length ? (
        <div style={{ marginTop: 16 }}>
          <strong>Connections</strong>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12, marginTop: 8 }}>
            {model.connections.map((connection: string, index: number) => (
              <div key={index} style={{ marginBottom: index < model.connections.length - 1 ? 8 : 0, fontFamily: 'monospace', fontSize: 12 }}>
                {connection}
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <details style={{ marginTop: 16 }}>
        <summary><strong>JSON Info</strong></summary>
        <pre style={{ background: '#0f172a', color: '#e2e8f0', padding: 12, borderRadius: 8, overflowX: 'auto' }}>{JSON.stringify(model, null, 2)}</pre>
      </details>
    </div>
  );
}

function SectionTable({ title, headers, rows }: { title: string; headers: string[]; rows: (string | number | boolean | null | undefined)[][] }) {
  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ fontWeight: 600, marginBottom: 6 }}>{title}</div>
      <div style={{ border: '1px solid #eee', borderRadius: 8, overflow: 'hidden' }}>
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${headers.length}, 1fr)`, background: '#fafafa', padding: '8px 12px', fontWeight: 600 }}>
          {headers.map((h) => <div key={h}>{h}</div>)}
        </div>
        {rows.length === 0 ? (
          <div style={{ padding: 12 }}>No data</div>
        ) : rows.map((r, i) => (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: `repeat(${headers.length}, 1fr)`, padding: '8px 12px', borderTop: '1px solid #eee' }}>
            {r.map((c, j) => <div key={j} style={{ whiteSpace: 'pre-wrap' }}>{String(c ?? '')}</div>)}
          </div>
        ))}
      </div>
    </div>
  );
}

function valueOf(obj: any, key: string) {
  return obj && key in obj ? obj[key] : '';
}
function rangeOf(p: any) {
  const range = p?.range;
  if (!range) return '';
  const min = range.min;
  const max = range.max;
  if (min == null && max == null) return '';
  return `${min ?? ''}..${max ?? ''}`;
}







