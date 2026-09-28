export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    model?: string;
    provider?: string;
    tool_result?: any;
    rag_results?: any;
  };
}

export interface UserMemory {
  key: string;
  value: any;
  memory_type: string;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  is_processed: boolean;
  created_at: string;
}

export interface ToolItem {
  id: string;
  name: string;
  type: string;
  description: string;
  enabled: boolean;
  parameters: {
    name: string;
    type: string;
    description: string;
    required: boolean;
  }[];
}
