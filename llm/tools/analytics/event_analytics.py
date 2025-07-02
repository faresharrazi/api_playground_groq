"""
Event Analytics Tool for Livestorm
"""

import re
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import StructuredTool
from ..base_client import LivestormBaseClient


class EventAnalyticsInput(BaseModel):
    """Input schema for event analytics"""
    include_sessions: Optional[bool] = Field(True, description="Whether to include session data in analysis")


class EventAnalyticsClient(LivestormBaseClient):
    """Client for Livestorm event analytics operations"""
    
    def get_comprehensive_analytics(self, **kwargs) -> str:
        """
        Get comprehensive analytics for all events including:
        - Total number of events
        - Number of ended events
        - Total number of sessions
        - Event status categorization
        """
        # Get all events
        params = {}
        if kwargs.get("include_sessions"):
            params["include"] = "sessions"
        
        data = self._make_request("GET", "events", params)
        if "error" in data:
            return f"Error: {data['error']}"
        
        complete_data = self._handle_pagination(data, params, "events")
        events = complete_data.get("data", [])
        
        # Analyze the data
        total_events = len(events)
        status_counts = {}
        total_sessions = 0
        ended_events = 0
        
        for event in events:
            attributes = event.get("attributes", {})
            status = attributes.get("scheduling_status", "unknown")
            
            # Count by status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count sessions
            sessions_count = attributes.get("sessions_count", 0)
            total_sessions += sessions_count
            
            # Count ended events specifically
            if status == "ended":
                ended_events += 1
        
        # Create status breakdown
        status_breakdown = []
        for status, count in sorted(status_counts.items()):
            percentage = (count / total_events * 100) if total_events > 0 else 0
            status_breakdown.append(f"• {status.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        # Format the response
        analytics_summary = f"""FINAL ANSWER: COMPREHENSIVE EVENT ANALYTICS

📊 OVERALL STATISTICS:
• Total Events: {total_events}
• Ended Events: {ended_events}
• Total Sessions: {total_sessions}
• Average Sessions per Event: {total_sessions/total_events:.1f} (if total_events > 0 else 0)

📈 EVENT STATUS BREAKDOWN:
{chr(10).join(status_breakdown)}

🎯 KEY METRICS:
• Ended Events Percentage: {ended_events/total_events*100:.1f}% (if total_events > 0 else 0)
• Active Events (not ended): {total_events - ended_events}
• Events with Sessions: {sum(1 for e in events if e.get('attributes', {}).get('sessions_count', 0) > 0)}

📋 DETAILED STATUS COUNTS:
{chr(10).join([f"  {status}: {count}" for status, count in sorted(status_counts.items())])}"""
        
        return analytics_summary


def create_event_analytics_tool(api_key: str) -> StructuredTool:
    """
    Create an event analytics tool
    
    Args:
        api_key: Livestorm API key
        
    Returns:
        StructuredTool for event analytics
    """
    client = EventAnalyticsClient(api_key)
    
    return StructuredTool(
        name="get_event_analytics",
        description="""Get comprehensive analytics for all Livestorm events. Returns detailed statistics including:
        - Total number of events
        - Number of ended events  
        - Total number of sessions across all events
        - Complete event status categorization with percentages
        - Key metrics and ratios
        
        This tool fetches ALL events and provides complete analytics in one call.""",
        args_schema=EventAnalyticsInput,
        func=client.get_comprehensive_analytics
    ) 