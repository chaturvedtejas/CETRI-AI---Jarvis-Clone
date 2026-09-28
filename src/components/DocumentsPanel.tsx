import React, { useState, useEffect } from 'react';
import { FileText, Upload, Trash2, Search, HelpCircle, CheckCircle, FileCode } from 'lucide-react';
import { DocumentItem } from '../types';

export const DocumentsPanel: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [askQuery, setAskQuery] = useState('');
  const [askResult, setAskResult] = useState<any>(null);
  const [asking, setAsking] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<any>(null);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents/list');
      const data = await res.json();
      if (data.documents) {
        setDocuments(data.documents);
      }
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.file_id) {
        fetchDocuments();
      }
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
      fetchDocuments();
      if (selectedDoc?.id === docId) setSelectedDoc(null);
    } catch (err) {
      console.error('Failed to delete doc:', err);
    }
  };

  const handleViewDetails = async (docId: string) => {
    try {
      const res = await fetch(`/api/documents/${docId}`);
      const data = await res.json();
      setSelectedDoc(data);
    } catch (err) {
      console.error('Failed to get doc details:', err);
    }
  };

  const handleAskRAG = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!askQuery.trim()) return;
    setAsking(true);
    setAskResult(null);

    try {
      const res = await fetch('/api/rag/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: askQuery.trim() })
      });
      const data = await res.json();
      setAskResult(data);
    } catch (err: any) {
      setAskResult({ has_context: false, message: err.message });
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950/70 border border-cyan-900/40 rounded-xl overflow-hidden p-5 backdrop-blur-md">
      <div className="flex items-center justify-between pb-4 border-b border-cyan-900/30">
        <div>
          <h2 className="text-lg font-tech font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" /> CETRI RAG ENGINE & DOCUMENT INTELLIGENCE
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Upload PDF, technical manuals, markdown files, and code. CETRI chunks and indexes them for contextual retrieval.
          </p>
        </div>

        <div>
          <label className="cursor-pointer py-2 px-3.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-xs font-tech tracking-wider rounded-lg transition-all flex items-center gap-1.5 shadow-md">
            <Upload className="w-3.5 h-3.5" />
            <span>{uploading ? 'INDEXING...' : 'INDEX DOCUMENT'}</span>
            <input
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mt-5 flex-1 overflow-hidden">
        {/* Document List */}
        <div className="flex flex-col bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4 overflow-hidden">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-mono uppercase text-slate-300 font-semibold">Indexed Knowledge Base</span>
            <span className="text-xs text-cyan-400 font-mono">{documents.length} files</span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {documents.length === 0 ? (
              <div className="text-center py-12 text-slate-500 font-mono text-xs">
                No documents uploaded. Click "Index Document" above to upload manuals, specifications, or notes.
              </div>
            ) : (
              documents.map(doc => (
                <div
                  key={doc.id}
                  onClick={() => handleViewDetails(doc.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                    selectedDoc?.id === doc.id
                      ? 'bg-cyan-950/70 border-cyan-400'
                      : 'bg-slate-950/70 border-cyan-900/40 hover:border-cyan-700/60'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 min-w-0 pr-2">
                    <FileCode className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                    <div className="min-w-0">
                      <div className="text-xs font-mono text-slate-200 truncate">{doc.filename}</div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {(doc.file_size / 1024).toFixed(1)} KB • {doc.file_type.toUpperCase()}
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(doc.id); }}
                    className="p-1 text-slate-500 hover:text-rose-400 rounded transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Document Preview or RAG Query */}
        <div className="lg:col-span-2 flex flex-col space-y-4 overflow-hidden">
          {/* RAG Ask Box */}
          <div className="bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4">
            <h3 className="text-xs font-mono uppercase text-slate-300 font-semibold mb-2 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400" /> RAG Natural Language Query
            </h3>

            <form onSubmit={handleAskRAG} className="flex gap-2">
              <input
                type="text"
                value={askQuery}
                onChange={e => setAskQuery(e.target.value)}
                placeholder="Ask CETRI questions grounded in your uploaded documents..."
                className="flex-1 p-2.5 bg-slate-950 border border-cyan-900/60 rounded text-xs text-cyan-200 font-mono outline-none focus:border-cyan-400"
              />
              <button
                type="submit"
                disabled={!askQuery.trim() || asking}
                className="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-slate-950 font-semibold text-xs font-tech tracking-wider rounded transition-all"
              >
                {asking ? 'QUERYING...' : 'QUERY RAG'}
              </button>
            </form>

            {askResult && (
              <div className="mt-3 p-3 bg-slate-950 border border-cyan-800/60 rounded text-xs font-mono text-slate-300">
                <div className="text-cyan-400 font-semibold mb-1 flex items-center gap-1">
                  <CheckCircle className="w-3.5 h-3.5 text-cyan-400" />
                  <span>RAG Synthesized Context:</span>
                </div>
                <div className="whitespace-pre-wrap leading-relaxed text-slate-200">
                  {askResult.context || askResult.message}
                </div>
                {askResult.sources && (
                  <div className="mt-2 text-[10px] text-slate-400">
                    Source Attribution: {askResult.sources.join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Document Content Inspection */}
          <div className="flex-1 bg-slate-900/60 border border-cyan-900/40 rounded-lg p-4 flex flex-col overflow-hidden">
            <span className="text-xs font-mono uppercase text-slate-300 font-semibold mb-2">
              {selectedDoc ? `Document Content Preview: ${selectedDoc.filename}` : 'Document Text Preview'}
            </span>

            <div className="flex-1 bg-slate-950/80 border border-cyan-950 rounded p-3 overflow-y-auto font-mono text-xs text-slate-300">
              {selectedDoc ? (
                <div className="space-y-2">
                  <div className="text-[11px] text-cyan-400 pb-2 border-b border-cyan-950">
                    ID: {selectedDoc.id} • Type: {selectedDoc.file_type} • Size: {selectedDoc.file_size} Bytes
                  </div>
                  <pre className="whitespace-pre-wrap leading-relaxed text-slate-200 font-mono text-xs">
                    {selectedDoc.extracted_text_preview || 'No text extracted.'}
                  </pre>
                </div>
              ) : (
                <div className="text-slate-500 text-center py-12">
                  Select a document from the left list to inspect extracted text tokens and chunking structure.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
