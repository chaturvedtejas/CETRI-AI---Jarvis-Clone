import React, { useState, useEffect } from 'react';
import { Calculator, CloudSun, Search, Cpu, Folder, Play, CheckCircle2, AlertCircle } from 'lucide-react';
import { ToolItem } from '../types';

export const ToolsPanel: React.FC = () => {
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [selectedToolId, setSelectedToolId] = useState<string>('calculator_001');
  const [args, setArgs] = useState<Record<string, any>>({
    expression: 'Math.sqrt(256) * 15',
    location: 'Tokyo',
    days: 3,
    query: 'CETRI AI Architecture',
    source: 'web',
    action: 'list',
    filename: 'security_protocol.txt',
    content: 'DEFENSE PROTOCOL ALPHA-1: All neural nodes secured.'
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/tools/list')
      .then(res => res.json())
      .then(data => {
        if (data.tools) setTools(data.tools);
      })
      .catch(err => console.error('Failed to load tools:', err));
  }, []);

  const handleExecute = async () => {
    setLoading(true);
    setResult(null);
    try {
      let body: any = {};
      if (selectedToolId === 'calculator_001') {
        body = { expression: args.expression };
      } else if (selectedToolId === 'weather_001') {
        body = { location: args.location, days: Number(args.days) || 1 };
      } else if (selectedToolId === 'search_001') {
        body = { query: args.query, source: args.source };
      } else if (selectedToolId === 'file_ops_001') {
        body = { action: args.action, filename: args.filename, content: args.content };
      } else if (selectedToolId === 'system_info_001') {
        body = {};
      }

      const res = await fetch(`/api/tools/execute/${selectedToolId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setResult({ success: false, error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const getToolIcon = (type: string) => {
    switch (type) {
      case 'calculator': return <Calculator className="w-5 h-5 text-amber-400" />;
      case 'weather': return <CloudSun className="w-5 h-5 text-cyan-400" />;
      case 'search': return <Search className="w-5 h-5 text-emerald-400" />;
      case 'file': return <Folder className="w-5 h-5 text-purple-400" />;
      default: return <Cpu className="w-5 h-5 text-sky-400" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950/70 border border-cyan-900/40 rounded-xl overflow-hidden p-5 backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-cyan-900/30">
        <div>
          <h2 className="text-lg font-tech font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" /> CETRI ACTION DISPATCHER & TOOL SUITE
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">Direct manual execution of operating system tools and auxiliary subsystems.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-5 flex-1 overflow-hidden">
        {/* Tool selector */}
        <div className="space-y-2 overflow-y-auto pr-1">
          <label className="text-xs font-mono uppercase text-slate-400 font-semibold">Select Subsystem Tool</label>
          <div className="space-y-2">
            {tools.map(tool => (
              <button
                key={tool.id}
                onClick={() => { setSelectedToolId(tool.id); setResult(null); }}
                className={`w-full text-left p-3 rounded-lg border transition-all flex items-start space-x-3 ${
                  selectedToolId === tool.id
                    ? 'bg-cyan-950/60 border-cyan-400 shadow-md shadow-cyan-950/40'
                    : 'bg-slate-900/60 border-cyan-900/30 hover:border-cyan-700/60'
                }`}
              >
                <div className="p-2 bg-slate-950 rounded-md border border-cyan-900/50">
                  {getToolIcon(tool.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-tech font-semibold text-slate-200 capitalize">{tool.name.replace(/_/g, ' ')}</div>
                  <div className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">{tool.description}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Input Parameters */}
        <div className="flex flex-col bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4 space-y-4">
          <label className="text-xs font-mono uppercase text-slate-400 font-semibold">Tool Arguments & Configuration</label>

          {selectedToolId === 'calculator_001' && (
            <div className="space-y-2">
              <label className="text-xs text-slate-300">Mathematical Expression</label>
              <input
                type="text"
                value={args.expression || ''}
                onChange={e => setArgs({ ...args, expression: e.target.value })}
                className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                placeholder="e.g. 42 * 7 or sqrt(144)"
              />
              <span className="text-[10px] text-slate-400">Supports basic arithmetic, sqrt, sin, cos, tan, log, pi.</span>
            </div>
          )}

          {selectedToolId === 'weather_001' && (
            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Target Location</label>
                <input
                  type="text"
                  value={args.location || ''}
                  onChange={e => setArgs({ ...args, location: e.target.value })}
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                  placeholder="e.g. Tokyo, London, San Francisco"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Forecast Horizon (Days)</label>
                <input
                  type="number"
                  min="1"
                  max="7"
                  value={args.days || 1}
                  onChange={e => setArgs({ ...args, days: e.target.value })}
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                />
              </div>
            </div>
          )}

          {selectedToolId === 'search_001' && (
            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Search Query</label>
                <input
                  type="text"
                  value={args.query || ''}
                  onChange={e => setArgs({ ...args, query: e.target.value })}
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                  placeholder="Enter keywords"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Source</label>
                <select
                  value={args.source || 'web'}
                  onChange={e => setArgs({ ...args, source: e.target.value })}
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                >
                  <option value="web">Web & External Archives</option>
                  <option value="wikipedia">Wikipedia</option>
                  <option value="knowledge_base">CETRI Neural Base</option>
                </select>
              </div>
            </div>
          )}

          {selectedToolId === 'file_ops_001' && (
            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs text-slate-300">Action</label>
                <select
                  value={args.action || 'list'}
                  onChange={e => setArgs({ ...args, action: e.target.value })}
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                >
                  <option value="list">List Virtual Workspace Files</option>
                  <option value="create">Create New File</option>
                  <option value="read">Read Existing File</option>
                </select>
              </div>

              {args.action !== 'list' && (
                <div className="space-y-1">
                  <label className="text-xs text-slate-300">Filename</label>
                  <input
                    type="text"
                    value={args.filename || ''}
                    onChange={e => setArgs({ ...args, filename: e.target.value })}
                    className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                    placeholder="e.g. mission_brief.txt"
                  />
                </div>
              )}

              {args.action === 'create' && (
                <div className="space-y-1">
                  <label className="text-xs text-slate-300">File Content</label>
                  <textarea
                    rows={3}
                    value={args.content || ''}
                    onChange={e => setArgs({ ...args, content: e.target.value })}
                    className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                    placeholder="Enter file text..."
                  />
                </div>
              )}
            </div>
          )}

          {selectedToolId === 'system_info_001' && (
            <div className="text-xs text-slate-400 py-3">
              No input required. Running this tool inspects the active operating environment, CPU specs, and runtime telemetry.
            </div>
          )}

          <div className="pt-2">
            <button
              onClick={handleExecute}
              disabled={loading}
              className="w-full py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 font-semibold font-tech tracking-wider rounded-lg transition-all flex items-center justify-center space-x-2"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{loading ? 'EXECUTING DIRECTIVE...' : 'EXECUTE TOOL'}</span>
            </button>
          </div>
        </div>

        {/* Output Telemetry */}
        <div className="flex flex-col bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4 overflow-hidden">
          <label className="text-xs font-mono uppercase text-slate-400 font-semibold mb-2 flex items-center justify-between">
            <span>Execution Telemetry</span>
            {result && (
              <span className={`text-[10px] flex items-center gap-1 ${result.success ? 'text-emerald-400' : 'text-rose-400'}`}>
                {result.success ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                {result.execution_time_ms ? `${result.execution_time_ms}ms` : ''}
              </span>
            )}
          </label>

          <div className="flex-1 bg-slate-950/80 border border-cyan-950 rounded p-3 overflow-y-auto font-mono text-xs text-slate-300">
            {loading ? (
              <div className="flex items-center space-x-2 text-cyan-400 py-6 justify-center">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span>Dispatching payload to tool runtime...</span>
              </div>
            ) : result ? (
              <pre className="whitespace-pre-wrap leading-relaxed text-cyan-200">
                {JSON.stringify(result, null, 2)}
              </pre>
            ) : (
              <div className="text-slate-500 text-center py-12">
                Output parameters will appear here upon execution.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
