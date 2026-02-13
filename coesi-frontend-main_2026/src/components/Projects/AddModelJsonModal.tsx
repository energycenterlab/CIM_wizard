import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import {
  ModelJson,
  validateModelJson,
  buildPreview,
  modelExists,
  upsertModel,
} from '../../utils/localModelStore';

export default function AddModelJsonModal({
  projectId,
  onClose,
  onAdded,
}: {
  projectId: string;
  onClose: () => void;
  onAdded: (model: ModelJson, replaced: boolean) => void;
}) {
  const [activeTab, setActiveTab] = useState<'upload' | 'code'>('upload');
  const [rawText, setRawText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [parsed, setParsed] = useState<ModelJson | null>(null);
  const [showReplace, setShowReplace] = useState<null | ModelJson>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Debounced validation for code tab
  useEffect(() => {
    if (activeTab !== 'code') return;
    const t = setTimeout(() => {
      if (!rawText.trim()) {
        setParsed(null);
        setError(null);
        return;
      }
      try {
        const obj = JSON.parse(rawText);
        const res = validateModelJson(obj);
        if (res.valid) {
          setParsed(res.parsed);
          setError(null);
        } else {
          setParsed(null);
          setError(`Invalid JSON: ${res.message}`);
        }
      } catch (e: any) {
        setParsed(null);
        setError(`Invalid JSON: ${e?.message || 'Parse error'}`);
      }
    }, 300);
    return () => clearTimeout(t);
  }, [rawText, activeTab]);

  const onDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    if (!e.dataTransfer.files?.length) return;
    await handleFile(e.dataTransfer.files[0]);
  };

  const handleFile = async (file: File) => {
    if (!file.name.endsWith('.json')) {
      setError('Invalid JSON: Only .json files are accepted');
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      setError('Invalid JSON: File exceeds 2 MB');
      return;
    }
    const text = await file.text();
    try {
      const obj = JSON.parse(text);
      const res = validateModelJson(obj);
      if (res.valid) {
        setParsed(res.parsed);
        setRawText(JSON.stringify(res.parsed, null, 2));
        setError(null);
        setActiveTab('code');
      } else {
        setParsed(null);
        setError(`Invalid JSON: ${res.message}`);
      }
    } catch (e: any) {
      setParsed(null);
      setError(`Invalid JSON: ${e?.message || 'Parse error'}`);
    }
  };

  const onChooseFile = () => fileInputRef.current?.click();
  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await handleFile(file);
    e.currentTarget.value = '';
  };

  const formatJson = () => {
    try {
      const obj = JSON.parse(rawText);
      setRawText(JSON.stringify(obj, null, 2));
    } catch {}
  };
  const clearJson = () => {
    setRawText('');
    setParsed(null);
    setError(null);
  };

  const preview = useMemo(() => (parsed ? buildPreview(parsed) : null), [parsed]);
  const canAdd = Boolean(parsed && !error);

  const handleAddModel = () => {
    if (!parsed) return;
    const exists = modelExists(projectId, parsed.name);
    if (exists && !showReplace) {
      setShowReplace(parsed);
      return;
    }
    const { replaced } = upsertModel(projectId, parsed);
    onAdded(parsed, replaced);
    onClose();
  };

  const replaceDialog = showReplace && (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100001 }}>
      <div style={{ background: 'white', padding: 16, borderRadius: 8, width: 420 }}>
        <h3 style={{ marginTop: 0 }}>Replace existing model?</h3>
        <p>A model named {showReplace.name} already exists. Do you want to replace it?</p>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button onClick={() => setShowReplace(null)} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 6, padding: '8px 12px' }}>No</button>
          <button onClick={() => { const { replaced } = upsertModel(projectId, showReplace); onAdded(showReplace, replaced); onClose(); }} style={{ background: '#2563eb', color: 'white', border: 'none', borderRadius: 6, padding: '8px 12px' }}>Replace</button>
        </div>
      </div>
    </div>
  );

  const content = (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100000 }} onClick={onClose}>
      <div onClick={(e) => e.stopPropagation()} style={{ background: 'white', width: 900, maxWidth: '95vw', maxHeight: '90vh', overflow: 'auto', borderRadius: 12 }}>
        <div style={{ padding: 16, borderBottom: '1px solid #eee' }}>
          <h2 style={{ margin: 0 }}>Add Model (JSON)</h2>
        </div>
        <div style={{ padding: 16 }}>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            <button onClick={() => setActiveTab('upload')} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd', background: activeTab === 'upload' ? '#eef2ff' : '#fff' }}>Upload JSON file</button>
            <button onClick={() => setActiveTab('code')} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd', background: activeTab === 'code' ? '#eef2ff' : '#fff' }}>Enter JSON code</button>
          </div>

          {activeTab === 'upload' ? (
            <div>
              <div
                onDrop={onDrop}
                onDragOver={(e) => e.preventDefault()}
                style={{ border: '2px dashed #cbd5e1', borderRadius: 12, padding: 24, textAlign: 'center', marginBottom: 12 }}
              >
                <div style={{ marginBottom: 8 }}>Drop a .json file here or choose a file (max 2 MB).</div>
                <button onClick={onChooseFile} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }}>Choose file</button>
                <input ref={fileInputRef} type="file" accept=".json" onChange={onFileChange} style={{ display: 'none' }} />
              </div>
              {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
            </div>
          ) : (
            <div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
                <button onClick={formatJson} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #ddd' }}>Format</button>
                <button onClick={clearJson} style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #ddd' }}>Clear</button>
              </div>
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                placeholder="Paste or type JSON here"
                style={{ width: '100%', minHeight: 260, fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace' }}
              />
              {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
            </div>
          )}

          {preview && (
            <div style={{ marginTop: 16, padding: 12, border: '1px solid #eee', borderRadius: 8 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>Preview</div>
              <div style={{ marginBottom: 6 }}>{preview.name}</div>
              <div style={{ color: '#666', marginBottom: 8 }}>{preview.description}</div>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Chip label={`Simulation: ${preview.simulationCount}`} />
                <Chip label={`Inputs: ${preview.inputCount}`} />
                <Chip label={`Outputs: ${preview.outputCount}`} />
                <Chip label={`Model params: ${preview.modelParamCount}`} />
              </div>
              {preview.possible?.length ? (
                <div style={{ marginTop: 8, color: '#444' }}>
                  Allowed connections: {preview.possible.join(', ')}
                </div>
              ) : null}
              <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                This is a local schema. Backend connection will be added later.
              </div>
            </div>
          )}
        </div>
        <div style={{ padding: 16, borderTop: '1px solid #eee', display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button onClick={onClose} style={{ background: '#f5f5f5', border: '1px solid #ddd', borderRadius: 6, padding: '8px 12px' }}>Cancel</button>
          <button onClick={handleAddModel} disabled={!canAdd} style={{ background: canAdd ? '#2563eb' : '#94a3b8', color: 'white', border: 'none', borderRadius: 6, padding: '8px 12px' }}>Add model</button>
        </div>
      </div>
      {replaceDialog}
    </div>
  );

  return createPortal(content, document.body);
}

function Chip({ label }: { label: string }) {
  return (
    <span style={{ background: '#f1f5f9', color: '#334155', borderRadius: 12, padding: '4px 8px', fontSize: 12 }}>{label}</span>
  );
}














