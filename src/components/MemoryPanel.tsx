import React, { useState, useEffect } from 'react';
import { Database, Plus, Trash2, Key, Search, RefreshCw } from 'lucide-react';
import { UserMemory } from '../types';

export const MemoryPanel: React.FC = () => {
  const [memories, setMemories] = useState<UserMemory[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newType, setNewType] = useState('preference');

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/memory/all');
      const data = await res.json();
      if (data.memories) {
        setMemories(data.memories);
      }
    } catch (err) {
      console.error('Failed to load memories:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;

    try {
      await fetch('/api/memory/store', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          key: newKey.trim(),
          value: newValue.trim(),
          memory_type: newType
        })
      });
      setNewKey('');
      setNewValue('');
      fetchMemories();
    } catch (err) {
      console.error('Failed to store memory:', err);
    }
  };

  const handleDeleteMemory = async (key: string) => {
    try {
      await fetch(`/api/memory/${encodeURIComponent(key)}`, {
        method: 'DELETE'
      });
      fetchMemories();
    } catch (err) {
      console.error('Failed to delete memory:', err);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to clear all CETRI persistent memories?')) return;
    try {
      await fetch('/api/memory/all', {
        method: 'DELETE'
      });
      fetchMemories();
    } catch (err) {
      console.error('Failed to clear memories:', err);
    }
  };

  const filteredMemories = memories.filter(m =>
    m.key.toLowerCase().includes(search.toLowerCase()) ||
    String(m.value).toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full bg-slate-950/70 border border-cyan-900/40 rounded-xl overflow-hidden p-5 backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-cyan-900/30">
        <div>
          <h2 className="text-lg font-tech font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" /> CETRI PERSISTENT MEMORY MATRIX
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Contextual state retention: CETRI remembers facts, directives, and user configurations across interactions.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={fetchMemories}
            className="p-2 bg-slate-900 hover:bg-cyan-950/60 border border-cyan-900/60 rounded-lg text-cyan-400 text-xs flex items-center gap-1.5 transition-colors"
            title="Refresh memory store"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sync</span>
          </button>
          <button
            onClick={handleClearAll}
            className="p-2 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/60 rounded-lg text-rose-300 text-xs flex items-center gap-1.5 transition-colors"
            title="Purge all memories"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Purge Matrix</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mt-5 flex-1 overflow-hidden">
        {/* Memory Insertion Form */}
        <div className="bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4 flex flex-col space-y-3">
          <h3 className="text-xs font-mono uppercase text-slate-300 font-semibold flex items-center gap-1.5">
            <Plus className="w-3.5 h-3.5 text-cyan-400" /> Store Neural Memory
          </h3>
          <p className="text-[11px] text-slate-400">
            You can also tell CETRI in chat: "Remember my favorite IDE is VS Code".
          </p>

          <form onSubmit={handleAddMemory} className="space-y-3 mt-1 flex-1 flex flex-col justify-between">
            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs text-slate-300 font-mono">Memory Key</label>
                <input
                  type="text"
                  value={newKey}
                  onChange={e => setNewKey(e.target.value)}
                  placeholder="e.g. coffee_preference"
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-300 font-mono">Value / Information</label>
                <textarea
                  rows={3}
                  value={newValue}
                  onChange={e => setNewValue(e.target.value)}
                  placeholder="e.g. Black with double espresso shot"
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs text-slate-300 font-mono">Classification</label>
                <select
                  value={newType}
                  onChange={e => setNewType(e.target.value)}
                  className="w-full p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-sm text-cyan-200 font-mono outline-none focus:border-cyan-400"
                >
                  <option value="preference">Preference</option>
                  <option value="user_fact">User Fact</option>
                  <option value="directive">System Directive</option>
                  <option value="security">Security Credential</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={!newKey.trim() || !newValue.trim()}
              className="w-full py-2.5 px-4 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 font-semibold font-tech tracking-wider rounded-lg transition-all flex items-center justify-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>COMMIT TO MEMORY</span>
            </button>
          </form>
        </div>

        {/* Memories List */}
        <div className="lg:col-span-2 flex flex-col bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4 overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <div className="relative flex-1 mr-3">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search stored memory keys or values..."
                className="w-full py-2 pl-9 pr-3 bg-slate-950 border border-cyan-900/60 rounded text-xs text-slate-200 placeholder-slate-500 font-mono outline-none focus:border-cyan-400"
              />
            </div>
            <span className="text-xs text-slate-400 font-mono">{filteredMemories.length} entries</span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2.5 pr-1">
            {filteredMemories.length === 0 ? (
              <div className="text-center py-12 text-slate-500 font-mono text-xs">
                No memories recorded in this sector.
              </div>
            ) : (
              filteredMemories.map(mem => (
                <div
                  key={mem.key}
                  className="p-3 bg-slate-950/80 border border-cyan-900/40 rounded-lg flex items-start justify-between hover:border-cyan-700/60 transition-colors"
                >
                  <div className="space-y-1 min-w-0 pr-3">
                    <div className="flex items-center space-x-2">
                      <Key className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="font-mono text-xs font-bold text-cyan-300 uppercase tracking-wide">
                        {mem.key}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-800 text-cyan-400">
                        {mem.memory_type}
                      </span>
                    </div>
                    <div className="text-xs text-slate-200 font-mono pl-5 break-words">
                      {String(mem.value)}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono pl-5">
                      Logged: {new Date(mem.created_at).toLocaleString()}
                    </div>
                  </div>

                  <button
                    onClick={() => handleDeleteMemory(mem.key)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 rounded transition-colors"
                    title="Delete record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
