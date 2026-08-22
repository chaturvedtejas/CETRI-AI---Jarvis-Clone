"""
Shared AI Service Layer

This service is the single brain used by:
- Frontend (Next.js)
- Desktop Assistant (main.py)
- Command-line interface

Every interaction flows through this unified service.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore

from config.settings import settings
from services.tool_service import get_tool_manager
from services.rag_service import get_rag_service


class MessageRole(str, Enum):
    """Message sender role"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIMessage:
    """Represents a single message in a conversation"""

    def __init__(
        self,
        content: str,
        role: MessageRole,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.content = content
        self.role = role
        self.timestamp = timestamp or datetime.utcnow()
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "role": self.role.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class ConversationContext:
    """Manages conversation context and memory"""

    def __init__(self, user_id: str, conversation_id: str):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.messages: List[AIMessage] = []
        self.user_memory: Dict[str, Any] = {}
        self.session_metadata: Dict[str, Any] = {}

    def add_message(self, message: AIMessage) -> None:
        """Add a message to conversation history"""
        self.messages.append(message)

    def get_recent_context(self, limit: int = 10) -> List[AIMessage]:
        """Get last N messages for context"""
        return self.messages[-limit:]

    def set_memory(self, key: str, value: Any) -> None:
        """Store user preference or memory"""
        self.user_memory[key] = value

    def get_memory(self, key: str) -> Optional[Any]:
        """Retrieve stored user memory"""
        return self.user_memory.get(key)


class AIService:
    """
    Unified AI Service Layer

    Provides:
    - Response generation
    - Conversation management
    - Memory retrieval
    - Context awareness

    Every request goes through here.
    """

    def __init__(self):
        self.active_conversations: Dict[str, ConversationContext] = {}
        self._openai_client: Optional[OpenAI] = None

    def _get_openai_client(self) -> Optional[OpenAI]:
        if not settings.openai_api_key or OpenAI is None:
            return None

        if self._openai_client is None:
            self._openai_client = OpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    def _build_prompt_messages(
        self,
        message: str,
        context: ConversationContext,
        additional_context: Optional[str] = None,
        tool_output: Optional[str] = None,
        explicit_context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        system_prompt = (
            "You are CETRI, a helpful AI assistant. Keep answers concise, practical, and clear. "
            "If the user asks for code or operations, provide direct, useful guidance."
        )

        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

        for prior in context.get_recent_context(limit=8):
            if prior.content:
                messages.append({"role": prior.role.value, "content": prior.content})

        prompt_text = message
        if additional_context:
            prompt_text = f"{prompt_text}\n\nRelevant document context:\n{additional_context}"
        if tool_output:
            prompt_text = f"{prompt_text}\n\nTool output:\n{tool_output}"
        if explicit_context:
            prompt_text = f"{prompt_text}\n\nAdditional context:\n{json.dumps(explicit_context, ensure_ascii=False)}"

        messages.append({"role": "user", "content": prompt_text})
        return messages

    async def _generate_llm_response(
        self,
        message: str,
        context: ConversationContext,
        additional_context: Optional[str] = None,
        tool_output: Optional[str] = None,
        explicit_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        client = self._get_openai_client()
        if client is None:
            raise RuntimeError(
                "OpenAI API key is not configured. Set OPENAI_API_KEY before starting the backend."
            )

        messages = self._build_prompt_messages(
            message=message,
            context=context,
            additional_context=additional_context,
            tool_output=tool_output,
            explicit_context=explicit_context,
        )

        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=600,
        )

        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI returned an empty response.")

        return content.strip()

    async def generate_response(
        self,
        user_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        use_rag: bool = False,
        tool_id: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Generate AI response
        """

        if conversation_id is None:
            conversation_id = f"conv_{user_id}_{datetime.utcnow().timestamp()}"

        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = ConversationContext(
                user_id=user_id,
                conversation_id=conversation_id,
            )

        conv = self.active_conversations[conversation_id]
        user_msg = AIMessage(content=message, role=MessageRole.USER)
        conv.add_message(user_msg)

        metadata: Dict[str, Any] = {}
        tool_response_text = None
        retrieved_context = None
        tool_manager = get_tool_manager()
        rag_service = get_rag_service()

        if tool_id or self._detect_tool_request(message):
            selected_tool_id = tool_id or self._infer_tool_id(message)
            selected_args = tool_args or self._infer_tool_args(message, selected_tool_id)
            tool_result = await tool_manager.execute_tool(selected_tool_id, **selected_args)
            metadata["tool_result"] = tool_result.dict()
            if tool_result.success:
                tool_response_text = (
                    f"I used the {tool_result.tool_name} tool to help answer your request. "
                    f"Result: {tool_result.result}"
                )
            else:
                tool_response_text = (
                    f"I attempted to use the {tool_result.tool_name} tool, but it failed: {tool_result.error}"
                )

        if use_rag or self._detect_rag_query(message):
            await rag_service.initialize()
            chunks, retrieved_context = await rag_service.retrieve_context(query=message, top_k=top_k)
            metadata["rag_results"] = {
                "count": len(chunks),
                "chunks": [c["id"] for c in chunks],
            }

        try:
            response = await self._generate_llm_response(
                message=message,
                context=conv,
                additional_context=self._build_augmented_context(message, retrieved_context),
                tool_output=tool_response_text,
                explicit_context=context,
            )
            provider_name = "openai"
            model_name = settings.openai_model
        except Exception as exc:
            response = (
                "I could not reach the configured LLM. Please verify the OpenAI API key and backend configuration, "
                "then retry your request."
            )
            metadata["llm_error"] = str(exc)
            provider_name = "unconfigured"
            model_name = settings.openai_model

        assistant_msg = AIMessage(
            content=response,
            role=MessageRole.ASSISTANT,
            metadata={
                "tool_used": bool(tool_response_text),
                "rag_used": bool(retrieved_context),
                **({"tool_output": tool_response_text} if tool_response_text else {}),
            },
        )
        conv.add_message(assistant_msg)

        return {
            "response": response,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
            "messages_count": len(conv.messages),
            "metadata": {
                "model": model_name,
                "provider": provider_name,
                "tokens": len(response.split()),
                "latency_ms": 100,
                **metadata,
            },
        }

    def _detect_tool_request(self, message: str) -> bool:
        candidate = message.lower()
        return any(
            keyword in candidate
            for keyword in [
                "weather",
                "forecast",
                "calculate",
                "calc",
                "search",
                "find",
                "what is",
                "who is",
                "where is",
            ]
        )

    def _infer_tool_id(self, message: str) -> str:
        candidate = message.lower()
        if "weather" in candidate or "forecast" in candidate:
            return "weather_001"
        if any(op in candidate for op in ["+", "-", "*", "/", "sqrt", "log", "sin", "cos"]):
            return "calculator_001"
        return "search_001"

    def _infer_tool_args(self, message: str, tool_id: str) -> Dict[str, Any]:
        candidate = message.strip()
        if tool_id == "weather_001":
            return {"location": candidate, "days": 1}
        if tool_id == "calculator_001":
            return {"expression": candidate}
        return {"query": candidate, "source": "web"}

    def _detect_rag_query(self, message: str) -> bool:
        candidate = message.lower()
        return any(
            keyword in candidate
            for keyword in [
                "document",
                "pdf",
                "report",
                "notes",
                "book",
                "article",
                "summarize",
                "summary",
                "what does",
                "what is",
                "who is",
            ]
        )

    def _build_augmented_context(self, message: str, retrieved_context: Optional[str]) -> str:
        if not retrieved_context:
            return message
        return (
            "Retrieved document context:\n"
            f"{retrieved_context}\n"
            "Use the information above to answer the user query.\n"
            f"User question: {message}"
        )

    async def retrieve_memory(self, user_id: str, key: str) -> Optional[Any]:
        """
        Retrieve stored user memory/preferences
        """
        for conv in self.active_conversations.values():
            if conv.user_id == user_id:
                return conv.get_memory(key)
        return None

    async def store_memory(self, user_id: str, key: str, value: Any) -> bool:
        """
        Store user memory/preferences
        """
        for conv in self.active_conversations.values():
            if conv.user_id == user_id:
                conv.set_memory(key, value)
                return True
        return False

    async def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if conversation_id not in self.active_conversations:
            return []

        conv = self.active_conversations[conversation_id]
        messages = conv.messages[-limit:]
        return [msg.to_dict() for msg in messages]

    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history"""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
            return True
        return False


_ai_service_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create singleton AI service"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
