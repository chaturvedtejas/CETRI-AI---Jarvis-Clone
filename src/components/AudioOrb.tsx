import React from 'react';

interface AudioOrbProps {
  isListening: boolean;
  isSpeaking: boolean;
  onOrbClick?: () => void;
}

export const AudioOrb: React.FC<AudioOrbProps> = ({ isListening, isSpeaking, onOrbClick }) => {
  return (
    <div 
      onClick={onOrbClick}
      className="relative flex items-center justify-center w-44 h-44 cursor-pointer group select-none"
      title={isListening ? "Listening... click to stop" : "Click to speak with CETRI"}
    >
      {/* Outer Ring 1: Radar sweep */}
      <div className={`absolute inset-0 rounded-full border border-cyan-500/20 ${isListening || isSpeaking ? 'animate-radar border-cyan-400/50' : ''}`} />
      
      {/* Outer Ring 2: Dash pattern */}
      <div className={`absolute inset-2 rounded-full border border-dashed border-cyan-500/30 ${isListening ? 'animate-spin border-cyan-400' : 'animate-[spin_20s_linear_infinite]'}`} />
      
      {/* Pulsing Aura */}
      <div className={`absolute inset-6 rounded-full bg-cyan-500/10 transition-all duration-500 ${
        isListening 
          ? 'scale-125 bg-amber-500/20 border border-amber-400 animate-pulse' 
          : isSpeaking 
          ? 'scale-115 bg-cyan-400/25 border border-cyan-300 animate-pulse-ring' 
          : 'group-hover:scale-105 group-hover:bg-cyan-500/20'
      }`} />

      {/* Rotating Arc Segments */}
      <svg className="absolute inset-4 w-36 h-36 animate-[spin_12s_linear_infinite]" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="44"
          fill="none"
          stroke={isListening ? "#f59e0b" : "#06b6d4"}
          strokeWidth="2.5"
          strokeDasharray="25 15 40 20"
          className="opacity-70"
        />
      </svg>

      <svg className="absolute inset-6 w-32 h-32 animate-[spin_8s_linear_infinite_reverse]" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke={isSpeaking ? "#38bdf8" : "#0ea5e9"}
          strokeWidth="1.5"
          strokeDasharray="15 35 10 30"
          className="opacity-60"
        />
      </svg>

      {/* Central Core Arc Reactor */}
      <div className={`relative flex items-center justify-center w-20 h-20 rounded-full transition-all duration-300 shadow-lg ${
        isListening
          ? 'bg-amber-950/80 border-2 border-amber-400 shadow-amber-500/50'
          : isSpeaking
          ? 'bg-cyan-950/90 border-2 border-cyan-300 shadow-cyan-400/60'
          : 'bg-slate-900/90 border border-cyan-500/40 group-hover:border-cyan-400 shadow-cyan-500/20'
      }`}>
        {/* Core waveform spikes or pulsing dot */}
        <div className="flex items-center space-x-1">
          <span className={`w-1 rounded-full transition-all duration-150 ${isListening ? 'h-6 bg-amber-400 animate-bounce' : isSpeaking ? 'h-8 bg-cyan-300 animate-pulse' : 'h-3 bg-cyan-500/60'}`} />
          <span className={`w-1 rounded-full transition-all duration-150 ${isListening ? 'h-10 bg-amber-300 animate-bounce [animation-delay:100ms]' : isSpeaking ? 'h-11 bg-cyan-200 animate-pulse [animation-delay:150ms]' : 'h-5 bg-cyan-400/80'}`} />
          <span className={`w-1 rounded-full transition-all duration-150 ${isListening ? 'h-8 bg-amber-400 animate-bounce [animation-delay:200ms]' : isSpeaking ? 'h-9 bg-cyan-300 animate-pulse [animation-delay:300ms]' : 'h-4 bg-cyan-500/60'}`} />
        </div>

        {/* Small label inside orb */}
        <span className="absolute bottom-1.5 text-[8px] tracking-widest uppercase font-mono text-cyan-400/80">
          {isListening ? 'REC' : isSpeaking ? 'VOX' : 'CETRI'}
        </span>
      </div>
    </div>
  );
};
