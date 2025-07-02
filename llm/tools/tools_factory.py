"""
Factory for creating Livestorm API tools
"""

from typing import List
from langchain.tools import Tool
from .events.list_events import create_list_events_tool
from .analytics.event_analytics import create_event_analytics_tool


def create_livestorm_tools(api_key: str) -> List[Tool]:
    """
    Create all available Livestorm API tools
    
    Args:
        api_key: Livestorm API key
        
    Returns:
        List of LangChain Tool objects
    """
    tools = []
    
    # Events tools
    tools.append(create_list_events_tool(api_key))
    tools.append(create_event_analytics_tool(api_key))
    
    # TODO: Add more tools as they are implemented
    # tools.append(create_get_event_tool(api_key))
    # tools.append(create_list_sessions_tool(api_key))
    # tools.append(create_list_people_tool(api_key))
    
    return tools 