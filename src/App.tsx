import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Cpu, Database, FileText, Volume2, VolumeX, Shield, Activity, Radio, HelpCircle } from 'lucide-react';
import { AudioOrb } from './components/AudioOrb';
import { TerminalChat } from './components/TerminalChat';
import { ToolsPanel } from './components/ToolsPanel';
import { MemoryPanel } from './components/MemoryPanel';
import { DocumentsPanel } from './components/DocumentsPanel';
import { ChatMessage } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<'terminal' | 'tools' | 'memory' | 'documents'>('terminal');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [conversationId] = useState<string>(() => `conv_cetri_${Date.now()}`);

  const recognitionRef = useRef<any>(null);

  // Initial greeting from CETRI matching main.py
  useEffect(() => {
    const welcomeMsg: ChatMessage = {
      id: 'msg_welcome',
      role: 'assistant',
      content: `CETRI v2.0 AI Assistant Online.\nInspired by JARVIS. Subsystems loaded: Voice I/O, NLP Brain, RAG Retrieval, Action Dispatcher.\nReady for your directives. Speak via microphone or type below.`,
      timestamp: new Date().toISOString(),
      metadata: {
        model: 'cetri-kernel-v2',
        provider: 'cetri-hybrid'
      }
    };
    setMessages([welcomeMsg]);
  }, []);

  // Web Speech API: Text-to-Speech
  const speakText = (text: string) => {
    if (!voiceEnabled || typeof window === 'undefined' || !window.speechSynthesis) return;

    window.speechSynthesis.cancel(); // Stop any pending speech

    // Remove markdown symbols and bullet stars for cleaner speech
    const cleanSpeech = text
      .replace(/[#*_`]/g, '')
      .replace(/https?:\/\/\S+/g, 'link')
      .replace(/[•-]/g, '')
      .slice(0, 300); // Keep voice summary concise

    const utterance = new SpeechSynthesisUtterance(cleanSpeech);
    utterance.rate = 1.05;
    utterance.pitch = 0.95;

    // Pick English British or best voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('UK') || v.name.includes('Daniel') || v.name.includes('Natural') || v.name.includes('Google'))) || voices[0];
    if (preferredVoice) utterance.voice = preferredVoice;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  };

  // Web Speech API: Speech Recognition
  const toggleListening = () => {
    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
      return;
    }

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported on this browser. You can type commands in the terminal directly.');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };

      recognition.onresult = (event: any) => {
        const current = event.resultIndex;
        const text = event.results[current][0].transcript;
        setTranscript(text);

        if (event.results[current].isFinal) {
          handleSendMessage(text);
          setIsListening(false);
        }
      };

      recognition.onerror = (err: any) => {
        console.warn('Speech recognition error:', err);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      setIsListening(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'usr_cetri_admin',
          message: text,
          conversation_id: conversationId,
          use_rag: activeTab === 'documents'
        })
      });

      const data = await res.json();

      const assistantMessage: ChatMessage = {
        id: `msg_a_${Date.now()}`,
        role: 'assistant',
        content: data.response || "Directive processed.",
        timestamp: data.timestamp || new Date().toISOString(),
        metadata: data.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Speak response aloud if audio enabled
      if (voiceEnabled && data.response) {
        speakText(data.response);
      }
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: `msg_err_${Date.now()}`,
        role: 'assistant',
        content: `Subsystem Communication Error: ${err.message}`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([]);
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-100 flex flex-col font-mono selection:bg-cyan-500/30 selection:text-cyan-200 relative overflow-hidden jarvis-grid">
      {/* Top Holographic Navigation Bar */}
      <header className="h-16 border-b border-cyan-900/40 bg-slate-950/80 backdrop-blur-md px-6 flex items-center justify-between z-20">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-500/50 flex items-center justify-center glow-cyan-sm">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-tech font-bold text-lg text-cyan-300 tracking-wider">CETRI AI</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-700/60 text-cyan-400 font-mono">v2.0 OS</span>
            </div>
            <p className="text-[10px] text-slate-400 tracking-tight hidden sm:block">Intelligent Operating Assistant • JARVIS Protocol</p>
          </div>
        </div>

        {/* Tab Controls */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('terminal')}
            className={`px-3 py-1.5 rounded-lg text-xs font-tech font-semibold tracking-wider transition-all flex items-center gap-1.5 ${
              activeTab === 'terminal'
                ? 'bg-cyan-950 border border-cyan-400 text-cyan-300 glow-cyan-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">TERMINAL</span>
          </button>

          <button
            onClick={() => setActiveTab('tools')}
            className={`px-3 py-1.5 rounded-lg text-xs font-tech font-semibold tracking-wider transition-all flex items-center gap-1.5 ${
              activeTab === 'tools'
                ? 'bg-cyan-950 border border-cyan-400 text-cyan-300 glow-cyan-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">TOOLS</span>
          </button>

          <button
            onClick={() => setActiveTab('memory')}
            className={`px-3 py-1.5 rounded-lg text-xs font-tech font-semibold tracking-wider transition-all flex items-center gap-1.5 ${
              activeTab === 'memory'
                ? 'bg-cyan-950 border border-cyan-400 text-cyan-300 glow-cyan-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <Database className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">MEMORY</span>
          </button>

          <button
            onClick={() => setActiveTab('documents')}
            className={`px-3 py-1.5 rounded-lg text-xs font-tech font-semibold tracking-wider transition-all flex items-center gap-1.5 ${
              activeTab === 'documents'
                ? 'bg-cyan-950 border border-cyan-400 text-cyan-300 glow-cyan-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">RAG DOCS</span>
          </button>
        </nav>

        {/* System Status Indicators */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="hidden md:flex items-center space-x-2 px-2.5 py-1 rounded bg-slate-900/80 border border-cyan-900/40">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300 text-[11px]">KERNEL: NOMINAL</span>
          </div>

          <button
            onClick={() => setVoiceEnabled(!voiceEnabled)}
            className={`p-2 rounded-lg border transition-all ${
              voiceEnabled ? 'bg-cyan-950/80 border-cyan-400 text-cyan-300' : 'bg-slate-900 border-slate-700 text-slate-500'
            }`}
            title={voiceEnabled ? 'Audio Speech active' : 'Audio Speech muted'}
          >
            {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Main Operating Workspace */}
      <main className="flex-1 p-4 md:p-6 flex flex-col max-w-7xl w-full mx-auto overflow-hidden">
        {activeTab === 'terminal' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-6.5rem)]">
            {/* Left Holographic HUD Column */}
            <div className="lg:col-span-4 flex flex-col space-y-4">
              {/* Arc Reactor Audio Orb Card */}
              <div className="bg-slate-950/70 border border-cyan-900/40 rounded-xl p-6 flex flex-col items-center justify-center backdrop-blur-md relative overflow-hidden">
                <div className="absolute top-3 left-4 text-[10px] font-mono text-cyan-400 tracking-wider flex items-center gap-1.5">
                  <Activity className="w-3 h-3 text-cyan-400" />
                  <span>NEURAL CORE INTERFACE</span>
                </div>

                <div className="py-4">
                  <AudioOrb
                    isListening={isListening}
                    isSpeaking={isSpeaking}
                    onOrbClick={toggleListening}
                  />
                </div>

                <div className="text-center mt-2">
                  <div className="text-sm font-tech font-bold text-slate-200 uppercase tracking-wider">
                    {isListening ? 'LISTENING TO DIRECTIVE...' : isSpeaking ? 'SYNTHESIZING AUDIO...' : 'CETRI STANDING BY'}
                  </div>
                  <p className="text-[11px] text-cyan-400/80 font-mono mt-1">
                    {isListening ? 'Speak your command clearly into microphone' : 'Click orb or mic button to activate speech'}
                  </p>
                </div>
              </div>

              {/* Real-time System Metrics */}
              <div className="bg-slate-950/70 border border-cyan-900/40 rounded-xl p-4 flex-1 flex flex-col justify-between backdrop-blur-md font-mono text-xs">
                <div>
                  <div className="flex items-center justify-between pb-2 border-b border-cyan-900/30 text-cyan-400 font-tech font-bold">
                    <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5" /> SYSTEM TELEMETRY</span>
                    <span className="text-[10px] text-emerald-400 font-mono">100% HEALTH</span>
                  </div>

                  <div className="space-y-3 mt-3">
                    <div>
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>CPU Virtual Cores</span>
                        <span className="text-cyan-300">8 Cores Active</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-cyan-400 w-2/5 animate-pulse" />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                        <span>Memory Matrix</span>
                        <span className="text-cyan-300">Heap Nominal</span>
                      </div>
                      <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-400 w-1/3" />
                      </div>
                    </div>

                    <div className="pt-2 text-[11px] text-slate-400 space-y-1">
                      <div className="flex justify-between">
                        <span>Audio Feedback:</span>
                        <span className={voiceEnabled ? "text-cyan-400 font-semibold" : "text-slate-500"}>
                          {voiceEnabled ? "Web Speech Active" : "Muted"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>RAG Knowledge Index:</span>
                        <span className="text-cyan-400">Ready</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Protocol Security:</span>
                        <span className="text-emerald-400">Class 1 Verified</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-cyan-900/30 text-[10px] text-slate-400">
                  Inspired by JARVIS • CETRI OS 2.0
                </div>
              </div>
            </div>

            {/* Right Terminal Column */}
            <div className="lg:col-span-8 h-full">
              <TerminalChat
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
                isListening={isListening}
                onToggleListen={toggleListening}
                voiceEnabled={voiceEnabled}
                onToggleVoice={() => setVoiceEnabled(!voiceEnabled)}
                onClearHistory={handleClearHistory}
                transcript={transcript}
              />
            </div>
          </div>
        )}

        {activeTab === 'tools' && (
          <div className="h-[calc(100vh-6.5rem)]">
            <ToolsPanel />
          </div>
        )}

        {activeTab === 'memory' && (
          <div className="h-[calc(100vh-6.5rem)]">
            <MemoryPanel />
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="h-[calc(100vh-6.5rem)]">
            <DocumentsPanel />
          </div>
        )}
      </main>
    </div>
  );
}
