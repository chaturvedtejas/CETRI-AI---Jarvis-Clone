import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Volume2, VolumeX, Trash2, Cpu, Sparkles, Terminal as TerminalIcon } from 'lucide-react';
import { ChatMessage } from '../types';

interface TerminalChatProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  isListening: boolean;
  onToggleListen: () => void;
  voiceEnabled: boolean;
  onToggleVoice: () => void;
  onClearHistory: () => void;
  transcript: string;
}

export const TerminalChat: React.FC<TerminalChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
  isListening,
  onToggleListen,
  voiceEnabled,
  onToggleVoice,
  onClearHistory,
  transcript
}) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const quickCommands = [
    { label: 'System Info', cmd: 'System info' },
    { label: 'Time & Date', cmd: 'What time and date is it?' },
    { label: 'Weather', cmd: 'Weather in Tokyo' },
    { label: 'Calculate', cmd: 'Calculate 144 * 12' },
    { label: 'List Files', cmd: 'List files in storage' },
    { label: 'Store Memory', cmd: 'Remember my protocol code is OMEGA-7' }
  ];

  return (
    <div className="flex flex-col h-full bg-slate-950/70 border border-cyan-900/40 rounded-xl overflow-hidden shadow-2xl backdrop-blur-md">
      {/* Console Top Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-900/80 border-b border-cyan-900/40 text-xs">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="text-cyan-400 font-tech font-semibold tracking-wider uppercase flex items-center gap-1.5 ml-2">
            <TerminalIcon className="w-3.5 h-3.5" /> CETRI_OS // COMMAND TERMINAL v2.0
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onToggleVoice}
            className={`p-1.5 rounded transition-all ${
              voiceEnabled ? 'text-cyan-400 bg-cyan-950/60 border border-cyan-800/60' : 'text-slate-500 hover:text-slate-300'
            }`}
            title={voiceEnabled ? 'Text-to-Speech active (click to mute)' : 'Muted (click to enable audio feedback)'}
          >
            {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
          <button
            onClick={onClearHistory}
            className="p-1.5 text-slate-500 hover:text-rose-400 rounded transition-colors"
            title="Purge session transcript"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Output Area */}
      <div ref={scrollRef} className="flex-1 p-4 overflow-y-auto space-y-4 font-mono text-sm scrollbar-thin scrollbar-thumb-cyan-950">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 py-12">
            <Cpu className="w-12 h-12 text-cyan-500/30 mb-3 animate-pulse" />
            <p className="text-cyan-400/80 font-tech text-base font-semibold">CETRI ASSISTANT READY</p>
            <p className="text-xs text-slate-400 mt-1 max-w-sm">
              Speak via voice input or send commands below. Supports file operations, calculations, memory, and telemetry.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className="flex items-center space-x-2 mb-1 px-1 text-[11px] text-slate-400">
              <span className={`font-semibold tracking-wider ${msg.role === 'user' ? 'text-amber-400' : 'text-cyan-400'}`}>
                {msg.role === 'user' ? 'USER_DIRECTIVE' : 'CETRI_CORE'}
              </span>
              <span>•</span>
              <span>{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
            </div>

            <div
              className={`p-3.5 rounded-lg max-w-[85%] whitespace-pre-wrap leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-amber-950/30 border border-amber-500/30 text-amber-100 rounded-tr-none'
                  : 'bg-cyan-950/20 border border-cyan-500/30 text-slate-200 rounded-tl-none shadow-sm'
              }`}
            >
              {msg.content}

              {/* Metadata Tags */}
              {msg.metadata && (
                <div className="mt-2.5 pt-2 border-t border-cyan-900/30 flex flex-wrap gap-2 text-[10px]">
                  {msg.metadata.model && (
                    <span className="px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-800 text-cyan-300">
                      ENG: {msg.metadata.model}
                    </span>
                  )}
                  {msg.metadata.tool_result && (
                    <span className="px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-800 text-emerald-300 flex items-center gap-1">
                      <Sparkles className="w-2.5 h-2.5" /> TOOL: {msg.metadata.tool_result.tool_name}
                    </span>
                  )}
                  {msg.metadata.rag_results && (
                    <span className="px-1.5 py-0.5 rounded bg-purple-950/80 border border-purple-800 text-purple-300">
                      RAG: {msg.metadata.rag_results.source || 'Knowledge indexed'}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex flex-col items-start">
            <div className="text-[11px] text-cyan-400 mb-1 px-1 font-semibold">CETRI_PROCESSING...</div>
            <div className="p-3 bg-cyan-950/20 border border-cyan-500/40 rounded-lg text-cyan-300 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="text-xs font-mono">Synthesizing telemetry & neural weights...</span>
            </div>
          </div>
        )}
      </div>

      {/* Quick Prompts Bar */}
      <div className="px-4 py-2 border-t border-cyan-900/30 bg-slate-900/40 flex items-center space-x-2 overflow-x-auto scrollbar-none text-xs">
        <span className="text-[10px] uppercase tracking-wider text-slate-500 font-mono flex-shrink-0">Quick Directives:</span>
        {quickCommands.map((qc) => (
          <button
            key={qc.label}
            onClick={() => onSendMessage(qc.cmd)}
            className="px-2.5 py-1 rounded bg-slate-900/90 border border-cyan-800/40 text-slate-300 hover:text-cyan-300 hover:border-cyan-400 hover:bg-cyan-950/40 transition-colors whitespace-nowrap text-xs flex-shrink-0"
          >
            {qc.label}
          </button>
        ))}
      </div>

      {/* Input Formulation Bar */}
      <form onSubmit={handleSubmit} className="p-3 bg-slate-900/90 border-t border-cyan-900/40 flex items-center space-x-2">
        <button
          type="button"
          onClick={onToggleListen}
          className={`p-2.5 rounded-lg border transition-all ${
            isListening
              ? 'bg-amber-500 text-slate-950 border-amber-300 animate-pulse'
              : 'bg-slate-800/80 border-cyan-800/50 text-cyan-400 hover:bg-cyan-950/60 hover:border-cyan-400'
          }`}
          title={isListening ? 'Listening... click to abort' : 'Activate Voice Command (Mic)'}
        >
          {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
        </button>

        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening for voice command..." : "Type directive or ask CETRI (e.g., 'What time is it?', 'calculate 42*7')..."}
            className="w-full py-2.5 px-3.5 bg-slate-950/90 border border-cyan-900/60 focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 rounded-lg text-sm text-slate-100 placeholder-slate-500 font-mono outline-none transition-all"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="p-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:hover:bg-cyan-600 text-slate-950 rounded-lg font-semibold transition-all shadow-md flex items-center justify-center"
          title="Dispatch Directive"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
