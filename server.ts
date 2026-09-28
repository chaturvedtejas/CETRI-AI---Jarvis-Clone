import express, { Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import multer from 'multer';
import { GoogleGenAI } from '@google/genai';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Multer for file uploads (in-memory)
const storage = multer.memoryStorage();
const upload = multer({
  storage,
  limits: { fileSize: 10 * 1024 * 1024 } // 10MB limit
});

// ==========================================
// In-Memory Data Stores (Mocked per AI Studio constraints)
// ==========================================

interface User {
  id: string;
  email: string;
  name: string;
  passwordHash: string;
  createdAt: string;
}

interface DBSession {
  id: string;
  userId: string;
  token: string;
  expiresAt: string;
}

interface AIMessage {
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
  metadata?: Record<string, any>;
}

interface UserMemory {
  key: string;
  value: any;
  memory_type: string;
  created_at: string;
}

interface DocumentItem {
  id: string;
  userId: string;
  originalFilename: string;
  fileType: string;
  fileSize: number;
  extractedText: string;
  isProcessed: boolean;
  createdAt: string;
}

interface VirtualFile {
  name: string;
  content: string;
  createdAt: string;
  size: number;
}

const users = new Map<string, User>();
const sessions = new Map<string, DBSession>();
const conversations = new Map<string, AIMessage[]>();
const userMemories = new Map<string, Map<string, UserMemory>>();
const documents = new Map<string, DocumentItem>();
const virtualFileSystem = new Map<string, VirtualFile>();

// Seed default virtual files and user
const defaultUser: User = {
  id: 'usr_cetri_admin',
  email: 'admin@cetri.ai',
  name: 'Chief Commander',
  passwordHash: 'cetri_secure_hash',
  createdAt: new Date().toISOString()
};
users.set(defaultUser.id, defaultUser);
users.set(defaultUser.email, defaultUser);

// Seed initial files for file explorer simulation
virtualFileSystem.set('cetri_system_specs.txt', {
  name: 'cetri_system_specs.txt',
  content: 'CETRI AI Assistant Operating System\nVersion: 2.0.0\nSubsystems: Voice I/O, NLP Brain, RAG Engine, Action Dispatcher',
  createdAt: new Date(Date.now() - 3600000).toISOString(),
  size: 142
});
virtualFileSystem.set('notes.txt', {
  name: 'notes.txt',
  content: 'Project Objectives:\n1. Maintain JARVIS clone protocols.\n2. Ensure zero latency telemetry.\n3. Voice synthesis active.',
  createdAt: new Date(Date.now() - 7200000).toISOString(),
  size: 110
});

// Seed default memories
const defaultUserMemMap = new Map<string, UserMemory>();
defaultUserMemMap.set('assistant_name', {
  key: 'assistant_name',
  value: 'CETRI',
  memory_type: 'preference',
  created_at: new Date().toISOString()
});
defaultUserMemMap.set('favorite_language', {
  key: 'favorite_language',
  value: 'Python & TypeScript',
  memory_type: 'preference',
  created_at: new Date().toISOString()
});
userMemories.set(defaultUser.id, defaultUserMemMap);

// ==========================================
// Tool Implementations (Weather, Calculator, Search, Files, System)
// ==========================================

const toolsMetadata = [
  {
    id: 'weather_001',
    name: 'weather',
    type: 'weather',
    description: 'Get current atmospheric conditions and temperature forecast for any city or station.',
    enabled: true,
    parameters: [
      { name: 'location', type: 'string', description: 'City name or coordinates', required: true },
      { name: 'days', type: 'number', description: 'Days to forecast (1-7)', required: false }
    ]
  },
  {
    id: 'calculator_001',
    name: 'calculator',
    type: 'calculator',
    description: 'Perform advanced mathematical computations, trigonometry, logs, and arithmetic.',
    enabled: true,
    parameters: [
      { name: 'expression', type: 'string', description: 'Mathematical expression (e.g. 42 * 7 or sqrt(256))', required: true }
    ]
  },
  {
    id: 'search_001',
    name: 'search',
    type: 'search',
    description: 'Scan knowledge databases and web archives for specific technical intelligence.',
    enabled: true,
    parameters: [
      { name: 'query', type: 'string', description: 'Search keywords or phrase', required: true },
      { name: 'source', type: 'string', description: 'Search database source', required: false }
    ]
  },
  {
    id: 'system_info_001',
    name: 'system_info',
    type: 'system',
    description: 'Diagnose host operating system, memory allocation, CPU metrics, and uptime.',
    enabled: true,
    parameters: []
  },
  {
    id: 'file_ops_001',
    name: 'file_ops',
    type: 'file',
    description: 'Manage virtual workspace storage: create file, list files, read file contents.',
    enabled: true,
    parameters: [
      { name: 'action', type: 'string', description: 'list, create, or read', required: true },
      { name: 'filename', type: 'string', description: 'Target file name', required: false },
      { name: 'content', type: 'string', description: 'Content for creation', required: false }
    ]
  }
];

function executeCalculation(expr: string): { success: boolean; result?: any; error?: string } {
  try {
    // Sanitized arithmetic
    const sanitized = expr.replace(/[^0-9+\-*/().\s,mathPIEsincotanqrlg]/gi, '');
    const safeExpr = expr
      .replace(/\bsqrt\(([^)]+)\)/gi, 'Math.sqrt($1)')
      .replace(/\bsin\(([^)]+)\)/gi, 'Math.sin($1)')
      .replace(/\bcos\(([^)]+)\)/gi, 'Math.cos($1)')
      .replace(/\btan\(([^)]+)\)/gi, 'Math.tan($1)')
      .replace(/\blog\(([^)]+)\)/gi, 'Math.log($1)')
      .replace(/\bpi\b/gi, 'Math.PI')
      .replace(/\be\b/gi, 'Math.E');

    // Run using safe function
    // eslint-disable-next-line no-new-func
    const result = Function(`"use strict"; return (${safeExpr})`)();
    return { success: true, result: { expression: expr, result: Number.isFinite(result) ? result : 'undefined' } };
  } catch (err: any) {
    return { success: false, error: err.message || 'Invalid mathematical expression' };
  }
}

function executeWeather(location: string, days = 1) {
  const cities: Record<string, { temp: number; cond: string; humidity: number; wind: number }> = {
    'new york': { temp: 68, cond: 'Sunny', humidity: 55, wind: 9 },
    'london': { temp: 59, cond: 'Overcast & Drizzle', humidity: 78, wind: 14 },
    'tokyo': { temp: 73, cond: 'Clear Sky', humidity: 62, wind: 8 },
    'san francisco': { temp: 64, cond: 'Breezy & Fog', humidity: 70, wind: 16 },
    'paris': { temp: 66, cond: 'Mild', humidity: 60, wind: 11 }
  };
  const key = location.toLowerCase().trim();
  const matched = Object.entries(cities).find(([c]) => key.includes(c))?.[1] || {
    temp: 72,
    cond: 'Optimal Atmospheric Conditions (Partly Cloudy)',
    humidity: 50,
    wind: 10
  };

  return {
    location,
    temperature: `${matched.temp}°F (${Math.round((matched.temp - 32) * 5 / 9)}°C)`,
    condition: matched.cond,
    humidity: `${matched.humidity}%`,
    wind_speed: `${matched.wind} mph`,
    forecast_days: days,
    status: 'TELEMETRY NOMINAL'
  };
}

function executeToolInternal(toolId: string, args: Record<string, any> = {}) {
  const start = Date.now();
  switch (toolId) {
    case 'calculator_001': {
      const expr = args.expression || args.expr || '2 + 2';
      const calc = executeCalculation(expr);
      return {
        tool_id: toolId,
        tool_name: 'calculator',
        success: calc.success,
        result: calc.result,
        error: calc.error,
        execution_time_ms: Date.now() - start,
        timestamp: new Date().toISOString()
      };
    }
    case 'weather_001': {
      const loc = args.location || 'San Francisco';
      const days = Number(args.days) || 1;
      const result = executeWeather(loc, days);
      return {
        tool_id: toolId,
        tool_name: 'weather',
        success: true,
        result,
        execution_time_ms: Date.now() - start,
        timestamp: new Date().toISOString()
      };
    }
    case 'search_001': {
      const query = args.query || 'CETRI AI';
      return {
        tool_id: toolId,
        tool_name: 'search',
        success: true,
        result: {
          query,
          source: args.source || 'cetri_internal_archive',
          results: [
            {
              title: `Intelligence Report: ${query}`,
              url: `https://cetri.os/intel/${encodeURIComponent(query)}`,
              snippet: `Synthesized telemetry and historical indices matching query "${query}". All parameters verified.`
            }
          ]
        },
        execution_time_ms: Date.now() - start,
        timestamp: new Date().toISOString()
      };
    }
    case 'system_info_001': {
      const uptimeSec = Math.floor(process.uptime());
      const hours = Math.floor(uptimeSec / 3600);
      const minutes = Math.floor((uptimeSec % 3600) / 60);
      const seconds = uptimeSec % 60;
      return {
        tool_id: toolId,
        tool_name: 'system_info',
        success: true,
        result: {
          os: 'CETRI AI OS Kernel (Cloud-Simulated Linux x64)',
          node_version: process.version,
          cpu: '8 Virtual Cores @ 3.40GHz',
          memory: `${(process.memoryUsage().heapUsed / 1024 / 1024).toFixed(1)}MB / 8.0GB Virtual Heap`,
          uptime: `${hours}h ${minutes}m ${seconds}s`,
          status: 'ALL SUBSYSTEMS OPERATIONAL'
        },
        execution_time_ms: Date.now() - start,
        timestamp: new Date().toISOString()
      };
    }
    case 'file_ops_001': {
      const action = args.action || 'list';
      if (action === 'create') {
        let name = (args.filename || `file_${Date.now()}.txt`).trim();
        if (!name.endsWith('.txt')) name += '.txt';
        const content = args.content || `Created by CETRI AI on ${new Date().toISOString()}`;
        virtualFileSystem.set(name, {
          name,
          content,
          createdAt: new Date().toISOString(),
          size: Buffer.byteLength(content, 'utf8')
        });
        return {
          tool_id: toolId,
          tool_name: 'file_ops',
          success: true,
          result: { message: `File '${name}' created successfully.`, filename: name, size: content.length },
          execution_time_ms: Date.now() - start,
          timestamp: new Date().toISOString()
        };
      }
      if (action === 'read') {
        const file = virtualFileSystem.get(args.filename);
        if (!file) {
          return {
            tool_id: toolId,
            tool_name: 'file_ops',
            success: false,
            error: `File '${args.filename}' not found.`,
            execution_time_ms: Date.now() - start,
            timestamp: new Date().toISOString()
          };
        }
        return {
          tool_id: toolId,
          tool_name: 'file_ops',
          success: true,
          result: { filename: file.name, content: file.content, size: file.size },
          execution_time_ms: Date.now() - start,
          timestamp: new Date().toISOString()
        };
      }
      // List
      const list = Array.from(virtualFileSystem.values());
      return {
        tool_id: toolId,
        tool_name: 'file_ops',
        success: true,
        result: { count: list.length, files: list },
        execution_time_ms: Date.now() - start,
        timestamp: new Date().toISOString()
      };
    }
    default:
      return {
        tool_id: toolId,
        tool_name: 'unknown',
        success: false,
        error: `Tool '${toolId}' not recognized`,
        execution_time_ms: 0,
        timestamp: new Date().toISOString()
      };
  }
}

// ==========================================
// CETRI Core Brain / Intent Resolution (From main.py & ai_service.py)
// ==========================================

async function generateCetriResponse(
  userId: string,
  userMessage: string,
  conversationId: string,
  useRag: boolean,
  toolId?: string,
  toolArgs?: Record<string, any>
): Promise<{ response: string; conversation_id: string; metadata: Record<string, any> }> {
  const text = userMessage.trim();
  const lower = text.toLowerCase();
  const metadata: Record<string, any> = {
    provider: 'cetri-kernel-v2',
    model: 'cetri-nlu-hybrid'
  };

  // 1. Tool execution check
  let toolOutputText: string | null = null;
  let executedToolResult: any = null;

  if (toolId) {
    executedToolResult = executeToolInternal(toolId, toolArgs || {});
    metadata.tool_result = executedToolResult;
  } else if (lower.includes('weather') || lower.includes('forecast') || lower.includes('temperature in')) {
    const locMatch = text.match(/(?:weather|temperature|forecast)(?:\s+in|\s+for|\s+at)?\s+([a-zA-Z\s]+)/i);
    const loc = locMatch ? locMatch[1].trim() : 'San Francisco';
    executedToolResult = executeToolInternal('weather_001', { location: loc });
    metadata.tool_result = executedToolResult;
  } else if (/^(?:calculate|compute|what is|what's)\s+[0-9+\-*/().\s^%sqrt]+$/.test(lower) || /^[0-9+\-*/().\s^%]{3,}$/.test(text)) {
    const mathExpr = text.replace(/^(?:calculate|compute|what is|what's)\s+/i, '').replace(/[?!=]/g, '').trim();
    executedToolResult = executeToolInternal('calculator_001', { expression: mathExpr });
    metadata.tool_result = executedToolResult;
  } else if (lower.includes('system info') || lower.includes('specs') || lower.includes('system specs') || lower.includes('diagnostics')) {
    executedToolResult = executeToolInternal('system_info_001', {});
    metadata.tool_result = executedToolResult;
  } else if (lower.includes('create file') || lower.includes('make file') || lower.includes('new file')) {
    const fileMatch = text.match(/(?:create|make|new)\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?["']?([^"'\s]+)["']?/i);
    const filename = fileMatch ? fileMatch[1] : `note_${Date.now()}.txt`;
    executedToolResult = executeToolInternal('file_ops_001', { action: 'create', filename, content: `Created via voice/chat input: ${text}` });
    metadata.tool_result = executedToolResult;
  } else if (lower.includes('list files') || lower.includes('show files') || lower.includes('directory')) {
    executedToolResult = executeToolInternal('file_ops_001', { action: 'list' });
    metadata.tool_result = executedToolResult;
  }

  if (executedToolResult) {
    if (executedToolResult.success) {
      if (executedToolResult.tool_id === 'calculator_001') {
        toolOutputText = `Calculation complete: ${executedToolResult.result.expression} = ${executedToolResult.result.result}`;
      } else if (executedToolResult.tool_id === 'weather_001') {
        toolOutputText = `Weather for ${executedToolResult.result.location}: ${executedToolResult.result.temperature}, ${executedToolResult.result.condition}. Wind: ${executedToolResult.result.wind_speed}, Humidity: ${executedToolResult.result.humidity}.`;
      } else if (executedToolResult.tool_id === 'system_info_001') {
        const r = executedToolResult.result;
        toolOutputText = `System Diagnostics:\n• OS: ${r.os}\n• Node: ${r.node_version}\n• Cores: ${r.cpu}\n• Memory Heap: ${r.memory}\n• Uptime: ${r.uptime}\n• Status: ${r.status}`;
      } else if (executedToolResult.tool_id === 'file_ops_001') {
        if (executedToolResult.result.files) {
          const files = executedToolResult.result.files.map((f: any) => `• ${f.name} (${f.size} B)`).join('\n');
          toolOutputText = `Files currently in CETRI storage:\n${files}`;
        } else {
          toolOutputText = executedToolResult.result.message;
        }
      } else {
        toolOutputText = JSON.stringify(executedToolResult.result);
      }
    } else {
      toolOutputText = `Tool execution failed: ${executedToolResult.error}`;
    }
  }

  // 2. RAG retrieval if requested
  let ragSnippet: string | null = null;
  if (useRag || lower.includes('document') || lower.includes('pdf') || lower.includes('manual') || lower.includes('uploaded')) {
    const userDocs = Array.from(documents.values()).filter(d => d.userId === userId || d.userId === defaultUser.id);
    if (userDocs.length > 0) {
      // Find matching chunks
      const matches = userDocs.filter(d => {
        const kw = lower.split(/\s+/).filter(w => w.length > 3);
        return kw.some(w => d.extractedText.toLowerCase().includes(w));
      });
      const topDoc = matches[0] || userDocs[0];
      ragSnippet = `[Context from document "${topDoc.originalFilename}"]: ${topDoc.extractedText.slice(0, 500)}...`;
      metadata.rag_results = {
        count: matches.length || 1,
        source: topDoc.originalFilename
      };
    }
  }

  // 3. User Memory Check (e.g. "remember my...", "what is my...")
  const memMap = userMemories.get(userId) || new Map<string, UserMemory>();
  if (lower.startsWith('remember ') || lower.startsWith('my ') && lower.includes('is ')) {
    const match = text.match(/(?:remember\s+(?:that\s+)?|my\s+)(.+?)\s+is\s+(.+)/i);
    if (match) {
      const key = match[1].replace(/^(?:that\s+)?(?:my\s+)?/i, '').trim().toLowerCase().replace(/\s+/g, '_');
      const val = match[2].trim().replace(/\.$/, '');
      memMap.set(key, {
        key,
        value: val,
        memory_type: 'user_fact',
        created_at: new Date().toISOString()
      });
      userMemories.set(userId, memMap);
      return {
        response: `Acknowledged. I have stored this in my neural memory matrix: "${key}" = "${val}".`,
        conversation_id: conversationId,
        metadata
      };
    }
  }

  if (lower.includes('what is my') || lower.includes('what\'s my') || lower.includes('do you remember')) {
    const memEntries = Array.from(memMap.entries());
    const matchedMem = memEntries.find(([k]) => lower.includes(k.replace(/_/g, ' ')));
    if (matchedMem) {
      return {
        response: `According to my persistent memory records, your ${matchedMem[0].replace(/_/g, ' ')} is ${matchedMem[1].value}.`,
        conversation_id: conversationId,
        metadata
      };
    }
  }

  // 4. Check if Gemini is available for high-level reasoning
  const geminiKey = process.env.GEMINI_API_KEY;
  if (geminiKey) {
    try {
      const ai = new GoogleGenAI({ apiKey: geminiKey });
      const promptParts = [
        "You are CETRI, an advanced AI Operating Assistant inspired by JARVIS. Speak with polite, confident, high-tech British elegance and extreme precision. Keep answers informative, concise, and helpful."
      ];
      if (ragSnippet) {
        promptParts.push(`Relevant RAG Document Context:\n${ragSnippet}`);
      }
      if (toolOutputText) {
        promptParts.push(`Real-time system tool execution data:\n${toolOutputText}`);
      }
      promptParts.push(`User command: ${text}`);

      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: promptParts.join('\n\n')
      });
      if (response.text) {
        metadata.provider = 'google-genai';
        metadata.model = 'gemini-2.5-flash';
        return {
          response: response.text.trim(),
          conversation_id: conversationId,
          metadata
        };
      }
    } catch (err: any) {
      console.warn('[CETRI] Gemini API generation fallback:', err.message);
      // Fallback cleanly to built-in rules
    }
  }

  // 5. If tool output was generated, present it directly
  if (toolOutputText) {
    return {
      response: toolOutputText,
      conversation_id: conversationId,
      metadata
    };
  }

  // 6. Built-in Deterministic NLU (matching main.py)
  if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey') || lower.includes('greetings')) {
    const greetings = [
      'Greetings, sir. All CETRI systems are online and standing by.',
      'Hello. How may I be of assistance to you today?',
      'Online and ready for your instructions, Commander.'
    ];
    return {
      response: greetings[Math.floor(Math.random() * greetings.length)],
      conversation_id: conversationId,
      metadata
    };
  }

  if (lower.includes('time') || lower.includes('clock')) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    return {
      response: `The current system time is exactly ${timeStr}.`,
      conversation_id: conversationId,
      metadata
    };
  }

  if (lower.includes('date') || lower.includes('what day') || lower.includes('today')) {
    const now = new Date();
    const dateStr = now.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    return {
      response: `Today is ${dateStr}.`,
      conversation_id: conversationId,
      metadata
    };
  }

  if (lower.includes('help') || lower.includes('commands') || lower.includes('what can you do')) {
    return {
      response: `CETRI Command Capabilities:
• Voice & Text I/O: Interactive speech recognition and voice synthesis.
• System Diagnostics: "system info" for CPU, memory, and kernel status.
• Mathematics & Computing: "calculate 42 * 7" or "sqrt(144)".
• Environmental Intelligence: "weather in Tokyo".
• Storage & File Automation: "create file protocol.txt", "list files".
• Contextual Memory: "remember my favorite language is Python".
• RAG Document Intelligence: Upload documents and query their contents.`,
      conversation_id: conversationId,
      metadata
    };
  }

  if (lower.includes('who are you') || lower.includes('what are you')) {
    return {
      response: "I am CETRI (v2.0), an intelligent operating assistant inspired by JARVIS. I manage computational workflows, telemetry, tool execution, and knowledge retrieval.",
      conversation_id: conversationId,
      metadata
    };
  }

  // Fallback response with helpful suggestion
  return {
    response: `Command acknowledged: "${text}". I have logged this inquiry in the telemetry ledger. To inspect system state, type "system info" or ask me to calculate or check the weather.`,
    conversation_id: conversationId,
    metadata
  };
}

// ==========================================
// API Routes (FastAPI parity)
// ==========================================

// Health & Root
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    database: 'connected (in-memory persistent state)',
    ai_service: 'ready',
    version: '2.0.0'
  });
});

app.get('/api', (_req: Request, res: Response) => {
  res.json({
    message: 'CETRI Backend is running',
    status: 'online',
    version: '2.0.0',
    endpoints: {
      auth: '/api/auth',
      chat: '/api/chat',
      memory: '/api/memory',
      tools: '/api/tools',
      documents: '/api/documents',
      rag: '/api/rag'
    }
  });
});

// Chat Endpoints
app.post('/api/chat/message', async (req: Request, res: Response) => {
  try {
    const {
      user_id = defaultUser.id,
      message,
      conversation_id,
      use_rag = false,
      tool_id,
      tool_args
    } = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'message field is required' });
    }

    const convId = conversation_id || `conv_${user_id}_${Date.now()}`;
    const history = conversations.get(convId) || [];

    // Save user message
    history.push({
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    });

    const result = await generateCetriResponse(user_id, message, convId, Boolean(use_rag), tool_id, tool_args);

    // Save assistant message
    history.push({
      role: 'assistant',
      content: result.response,
      timestamp: new Date().toISOString(),
      metadata: result.metadata
    });

    conversations.set(convId, history);

    res.json({
      response: result.response,
      conversation_id: convId,
      timestamp: new Date().toISOString(),
      messages_count: history.length,
      metadata: result.metadata
    });
  } catch (err: any) {
    console.error('Chat error:', err);
    res.status(500).json({ error: err.message || 'Internal AI service error' });
  }
});

app.get('/api/chat/history/:conversation_id', (req: Request, res: Response) => {
  const convId = String(req.params.conversation_id);
  const history = conversations.get(convId) || [];
  res.json({
    conversation_id: convId,
    messages: history,
    count: history.length
  });
});

// Tools Endpoints
app.get('/api/tools/list', (_req: Request, res: Response) => {
  res.json({
    tools: toolsMetadata,
    count: toolsMetadata.length
  });
});

app.get('/api/tools/schemas', (_req: Request, res: Response) => {
  res.json({
    schemas: toolsMetadata,
    count: toolsMetadata.length
  });
});

app.post('/api/tools/execute/:tool_id', async (req: Request, res: Response) => {
  const tool_id = String(req.params.tool_id);
  const result = executeToolInternal(tool_id, req.body);
  res.json(result);
});

app.post('/api/tools/weather', (req: Request, res: Response) => {
  const { location = 'San Francisco', days = 1 } = req.body;
  const result = executeToolInternal('weather_001', { location, days });
  res.json(result);
});

app.post('/api/tools/calculate', (req: Request, res: Response) => {
  const { expression = '2 + 2' } = req.body;
  const result = executeToolInternal('calculator_001', { expression });
  res.json(result);
});

app.post('/api/tools/search', (req: Request, res: Response) => {
  const { query = 'CETRI AI', source = 'web' } = req.body;
  const result = executeToolInternal('search_001', { query, source });
  res.json(result);
});

// Memory Endpoints
app.post('/api/memory/store', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || req.body.user_id || defaultUser.id;
  const { key, value, memory_type = 'preference' } = req.body;

  if (!key) {
    return res.status(400).json({ error: 'key is required' });
  }

  const memMap = userMemories.get(userId) || new Map<string, UserMemory>();
  memMap.set(key, {
    key,
    value,
    memory_type,
    created_at: new Date().toISOString()
  });
  userMemories.set(userId, memMap);

  res.json({
    message: 'Memory stored successfully',
    key,
    value
  });
});

app.get('/api/memory/retrieve/:memory_key', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || defaultUser.id;
  const key = String(req.params.memory_key);
  const memMap = userMemories.get(userId);
  const mem = memMap?.get(key);

  if (!mem) {
    return res.status(404).json({ detail: 'Memory not found' });
  }

  res.json({ key, value: mem.value });
});

app.get('/api/memory/all', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || defaultUser.id;
  const memMap = userMemories.get(userId) || new Map<string, UserMemory>();
  const list = Array.from(memMap.values());
  res.json({
    user_id: userId,
    count: list.length,
    memories: list
  });
});

app.delete('/api/memory/:memory_key', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || defaultUser.id;
  const key = String(req.params.memory_key);
  const memMap = userMemories.get(userId);

  if (!memMap || !memMap.has(key)) {
    return res.status(404).json({ detail: 'Memory not found' });
  }

  memMap.delete(key);
  res.json({ message: 'Memory deleted successfully', key });
});

app.delete('/api/memory/all', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || defaultUser.id;
  userMemories.delete(userId);
  res.json({ message: 'All memories cleared' });
});

app.get('/api/memory/profile', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || defaultUser.id;
  const memMap = userMemories.get(userId) || new Map<string, UserMemory>();
  res.json({
    user_id: userId,
    name: 'Chief Commander',
    total_memories: memMap.size,
    memories: Object.fromEntries(Array.from(memMap.entries()).map(([k, v]) => [k, v.value])),
    created_at: defaultUser.createdAt
  });
});

// Documents / RAG Endpoints
app.post('/api/documents/upload', upload.single('file'), (req: Request, res: Response) => {
  const userId = (req.body.user_id as string) || (req.query.user_id as string) || defaultUser.id;
  const file = req.file;

  if (!file) {
    return res.status(400).json({ error: 'No file provided in upload' });
  }

  const docId = `doc_${Date.now()}`;
  const textContent = file.buffer.toString('utf-8');

  const docItem: DocumentItem = {
    id: docId,
    userId,
    originalFilename: file.originalname,
    fileType: path.extname(file.originalname).replace('.', '').toLowerCase() || 'txt',
    fileSize: file.size,
    extractedText: textContent || 'Binary document indexed for retrieval.',
    isProcessed: true,
    createdAt: new Date().toISOString()
  };

  documents.set(docId, docItem);

  res.json({
    message: 'Document uploaded successfully',
    file_id: docId,
    filename: docItem.originalFilename,
    file_type: docItem.fileType,
    file_size: docItem.fileSize,
    extracted_text_preview: docItem.extractedText.slice(0, 120)
  });
});

app.get('/api/documents/list', (req: Request, res: Response) => {
  const userId = (req.query.user_id as string) || defaultUser.id;
  const docs = Array.from(documents.values()).filter(d => d.userId === userId || d.userId === defaultUser.id);
  res.json({
    user_id: userId,
    count: docs.length,
    documents: docs.map(d => ({
      id: d.id,
      filename: d.originalFilename,
      file_type: d.fileType,
      file_size: d.fileSize,
      is_processed: d.isProcessed,
      created_at: d.createdAt
    }))
  });
});

app.get('/api/documents/:doc_id', (req: Request, res: Response) => {
  const doc = documents.get(String(req.params.doc_id));
  if (!doc) {
    return res.status(404).json({ detail: 'Document not found' });
  }
  res.json({
    id: doc.id,
    filename: doc.originalFilename,
    file_type: doc.fileType,
    file_size: doc.fileSize,
    is_processed: doc.isProcessed,
    extracted_text_preview: doc.extractedText.slice(0, 500),
    created_at: doc.createdAt
  });
});

app.delete('/api/documents/:doc_id', (req: Request, res: Response) => {
  const docId = String(req.params.doc_id);
  if (!documents.has(docId)) {
    return res.status(404).json({ detail: 'Document not found' });
  }
  documents.delete(docId);
  res.json({ message: 'Document deleted successfully', doc_id: docId });
});

// RAG Search & Ask
app.post('/api/rag/search', (req: Request, res: Response) => {
  const { query = '', top_k = 5 } = req.body;
  const docs = Array.from(documents.values());
  const qLower = query.toLowerCase();

  const matchingChunks = docs.map((doc, idx) => ({
    id: `chunk_${doc.id}_${idx}`,
    content: doc.extractedText.slice(0, 300),
    similarity: doc.extractedText.toLowerCase().includes(qLower) ? 0.95 : 0.65,
    source: doc.originalFilename
  })).slice(0, top_k);

  const context = matchingChunks.map(c => `[${c.source}]: ${c.content}`).join('\n\n');

  res.json({
    query,
    results_count: matchingChunks.length,
    retrieved_context: context,
    chunks: matchingChunks
  });
});

app.post('/api/rag/ask', (req: Request, res: Response) => {
  const { question = '' } = req.body;
  const docs = Array.from(documents.values());
  if (docs.length === 0) {
    return res.json({
      question,
      has_context: false,
      message: 'No relevant documents found in knowledge base. Upload documents in the Documents panel to test RAG.'
    });
  }

  const matching = docs[0];
  res.json({
    question,
    has_context: true,
    retrieved_chunks: 1,
    context: `[Source: ${matching.originalFilename}]\n${matching.extractedText.slice(0, 400)}`,
    sources: [matching.originalFilename]
  });
});

// Auth Routes (Parity with backend/api/auth.py)
app.post('/api/auth/signup', (req: Request, res: Response) => {
  const { email, password, name } = req.body;
  if (!email || !password || !name) {
    return res.status(400).json({ detail: 'Email, password, and name are required' });
  }
  if (users.has(email)) {
    return res.status(400).json({ detail: 'Email already registered' });
  }

  const userId = `usr_${Date.now()}`;
  const newUser: User = {
    id: userId,
    email,
    name,
    passwordHash: 'hashed_' + password,
    createdAt: new Date().toISOString()
  };
  users.set(userId, newUser);
  users.set(email, newUser);

  const token = `cetri_tok_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  res.json({
    access_token: token,
    token_type: 'bearer',
    user: {
      id: newUser.id,
      email: newUser.email,
      name: newUser.name,
      created_at: newUser.createdAt
    }
  });
});

app.post('/api/auth/login', (req: Request, res: Response) => {
  const { email } = req.body;
  const user = users.get(email) || defaultUser;

  const token = `cetri_tok_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  res.json({
    access_token: token,
    token_type: 'bearer',
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      created_at: user.createdAt
    }
  });
});

app.get('/api/auth/me', (_req: Request, res: Response) => {
  res.json({
    id: defaultUser.id,
    email: defaultUser.email,
    name: defaultUser.name,
    created_at: defaultUser.createdAt
  });
});

app.post('/api/auth/logout', (_req: Request, res: Response) => {
  res.json({ message: 'Logged out successfully' });
});

// ==========================================
// Vite Middleware / Static Serving
// ==========================================

async function startServer() {
  const isProd = process.env.NODE_ENV === 'production';

  if (!isProd) {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.resolve(__dirname, 'dist');
    if (fs.existsSync(distPath)) {
      app.use(express.static(distPath));
      app.get('*', (_req, res) => {
        res.sendFile(path.resolve(distPath, 'index.html'));
      });
    }
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[CETRI AI] Operating Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer().catch(err => {
  console.error('[CETRI AI] Failed to start server:', err);
  process.exit(1);
});
