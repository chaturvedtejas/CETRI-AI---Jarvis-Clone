"""
Tool Calling Architecture

Allows CETRI to use external tools:
- Weather (get temperature, forecast)
- Calculator (math operations)
- Search (web search, Wikipedia)
- Email (send emails)
- Calendar (schedule events)
- File operations (read, write)

Tools are defined as schemas that the LLM can call.
"""

from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from pydantic import BaseModel
from abc import ABC, abstractmethod
import json
from datetime import datetime


class ToolType(str, Enum):
    """Types of tools CETRI can use"""
    WEATHER = "weather"
    CALCULATOR = "calculator"
    SEARCH = "search"
    EMAIL = "email"
    CALENDAR = "calendar"
    FILE = "file"
    DATABASE = "database"
    CODE = "code"


class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str
    type: str  # "string", "number", "boolean", "array"
    description: str
    required: bool = True
    enum: Optional[List[str]] = None  # For constrained values


class ToolSchema(BaseModel):
    """Schema for a tool that CETRI can call"""
    id: str
    name: str
    type: ToolType
    description: str
    parameters: List[ToolParameter]
    enabled: bool = True
    rate_limit: Optional[int] = None  # Calls per hour


class ToolResult(BaseModel):
    """Result from a tool execution"""
    tool_id: str
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float
    timestamp: str = None
    
    def __init__(self, **data):
        if data.get("timestamp") is None:
            data["timestamp"] = datetime.utcnow().isoformat()
        super().__init__(**data)


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, tool_id: str, name: str, description: str):
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.enabled = True
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """Get tool schema for LLM"""
        pass


class WeatherTool(BaseTool):
    """Get weather information"""
    
    def __init__(self):
        super().__init__(
            tool_id="weather_001",
            name="weather",
            description="Get current weather and forecast for a location"
        )
    
    async def execute(self, location: str, days: int = 1, **kwargs) -> ToolResult:
        """
        Get weather for a location
        
        Args:
            location: City name or coordinates
            days: Number of days to forecast (1-7)
        """
        import time
        start = time.time()
        
        try:
            # TODO: Replace with real API (OpenWeatherMap, WeatherAPI)
            result = {
                "location": location,
                "temperature": 72,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 12,
                "forecast_days": days
            }
            
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.name,
                success=True,
                result=result,
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            id=self.tool_id,
            name=self.name,
            type=ToolType.WEATHER,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="location",
                    type="string",
                    description="City name or coordinates",
                    required=True
                ),
                ToolParameter(
                    name="days",
                    type="number",
                    description="Days to forecast (1-7)",
                    required=False
                )
            ]
        )


class CalculatorTool(BaseTool):
    """Perform mathematical calculations"""
    
    def __init__(self):
        super().__init__(
            tool_id="calculator_001",
            name="calculator",
            description="Perform mathematical calculations"
        )
    
    async def execute(self, expression: str, **kwargs) -> ToolResult:
        """
        Calculate mathematical expression
        
        Args:
            expression: Math expression (e.g., "2 + 2", "sqrt(16)")
        """
        import time
        import math
        start = time.time()
        
        try:
            # Safe evaluation using allowed functions
            allowed_names = {
                "abs": abs,
                "round": round,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e
            }
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.name,
                success=True,
                result={
                    "expression": expression,
                    "result": result
                },
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            id=self.tool_id,
            name=self.name,
            type=ToolType.CALCULATOR,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="expression",
                    type="string",
                    description="Mathematical expression (e.g., '2 + 2')",
                    required=True
                )
            ]
        )


class SearchTool(BaseTool):
    """Search the web or knowledge base"""
    
    def __init__(self):
        super().__init__(
            tool_id="search_001",
            name="search",
            description="Search the web or knowledge base"
        )
    
    async def execute(self, query: str, source: str = "web", **kwargs) -> ToolResult:
        """
        Search for information
        
        Args:
            query: Search query
            source: "web", "wikipedia", or "knowledge_base"
        """
        import time
        start = time.time()
        
        try:
            # TODO: Replace with real API (Google Search, Wikipedia API)
            result = {
                "query": query,
                "source": source,
                "results": [
                    {
                        "title": f"Result for '{query}'",
                        "url": "https://example.com",
                        "snippet": f"Information about {query}..."
                    }
                ]
            }
            
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.name,
                success=True,
                result=result,
                execution_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return ToolResult(
                tool_id=self.tool_id,
                tool_name=self.name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def get_schema(self) -> ToolSchema:
        return ToolSchema(
            id=self.tool_id,
            name=self.name,
            type=ToolType.SEARCH,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True
                ),
                ToolParameter(
                    name="source",
                    type="string",
                    description="Search source",
                    required=False,
                    enum=["web", "wikipedia", "knowledge_base"]
                )
            ]
        )


class ToolManager:
    """Manages available tools and tool execution"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_default_tools()
    
    def _initialize_default_tools(self):
        """Initialize default tools"""
        default_tools = [
            WeatherTool(),
            CalculatorTool(),
            SearchTool(),
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool"""
        self.tools[tool.tool_id] = tool
        print(f"✓ Registered tool: {tool.name}")
    
    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Get a tool by ID"""
        return self.tools.get(tool_id)
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM"""
        return [
            tool.get_schema().dict()
            for tool in self.tools.values()
            if tool.enabled
        ]
    
    async def execute_tool(self, tool_id: str, **kwargs) -> ToolResult:
        """Execute a tool"""
        tool = self.get_tool(tool_id)
        if not tool:
            return ToolResult(
                tool_id=tool_id,
                tool_name="unknown",
                success=False,
                result=None,
                error=f"Tool not found: {tool_id}",
                execution_time_ms=0
            )
        
        if not tool.enabled:
            return ToolResult(
                tool_id=tool_id,
                tool_name=tool.name,
                success=False,
                result=None,
                error=f"Tool disabled: {tool.name}",
                execution_time_ms=0
            )
        
        return await tool.execute(**kwargs)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools"""
        return [
            {
                "id": tool.tool_id,
                "name": tool.name,
                "description": tool.description,
                "type": str(tool.get_schema().type),
                "enabled": tool.enabled
            }
            for tool in self.tools.values()
        ]


# Singleton instance
_tool_manager_instance: Optional[ToolManager] = None


def get_tool_manager() -> ToolManager:
    """Get or create singleton tool manager"""
    global _tool_manager_instance
    if _tool_manager_instance is None:
        _tool_manager_instance = ToolManager()
    return _tool_manager_instance
