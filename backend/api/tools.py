"""
Tools API endpoints

Exposes CETRI's tool capabilities via HTTP
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from services.tool_service import get_tool_manager

router = APIRouter()


@router.get("/list")
async def list_tools():
    """List all available tools"""
    tool_manager = get_tool_manager()
    tools = tool_manager.list_tools()
    return {
        "tools": tools,
        "count": len(tools)
    }


@router.get("/schemas")
async def get_tool_schemas():
    """Get tool schemas for LLM integration"""
    tool_manager = get_tool_manager()
    schemas = tool_manager.get_tool_schemas()
    return {
        "schemas": schemas,
        "count": len(schemas)
    }


@router.post("/execute/{tool_id}")
async def execute_tool(tool_id: str, **kwargs):
    """
    Execute a tool
    
    Args:
        tool_id: Tool identifier
        **kwargs: Tool parameters
    
    Example:
        POST /api/tools/execute/calculator_001
        {"expression": "2 + 2"}
    """
    tool_manager = get_tool_manager()
    result = await tool_manager.execute_tool(tool_id, **kwargs)
    
    return {
        "tool_id": result.tool_id,
        "tool_name": result.tool_name,
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "execution_time_ms": result.execution_time_ms,
        "timestamp": result.timestamp
    }


@router.post("/weather")
async def get_weather(location: str, days: int = 1):
    """Get weather for a location"""
    tool_manager = get_tool_manager()
    result = await tool_manager.execute_tool("weather_001", location=location, days=days)
    return result.dict()


@router.post("/calculate")
async def calculate(expression: str):
    """Calculate a math expression"""
    tool_manager = get_tool_manager()
    result = await tool_manager.execute_tool("calculator_001", expression=expression)
    return result.dict()


@router.post("/search")
async def search(query: str, source: str = "web"):
    """Search for information"""
    tool_manager = get_tool_manager()
    result = await tool_manager.execute_tool("search_001", query=query, source=source)
    return result.dict()
