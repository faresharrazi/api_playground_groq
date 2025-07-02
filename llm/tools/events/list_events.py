"""
List events tool for Livestorm API (StructuredTool version)
"""

from typing import Dict, List, Optional, Any, Union
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from ..base_client import LivestormBaseClient

class ListEventsInput(BaseModel):
    filter_title: Optional[str] = None
    filter_scheduling_status: Optional[str] = None
    filter_created_since: Optional[str] = None
    filter_created_until: Optional[str] = None
    filter_updated_since: Optional[str] = None
    filter_updated_until: Optional[str] = None
    include_sessions: Optional[bool] = None
    # page_number is ignored for full fetch
    page_number: Optional[str] = None

class EventsClient(LivestormBaseClient):
    """Client for Livestorm events operations"""
    
    def list_events(self, **kwargs):
        # Ignore page_number, always fetch all pages
        params = {}
        if kwargs.get("filter_title"):
            params["filter[title]"] = kwargs["filter_title"]
        if kwargs.get("filter_scheduling_status"):
            params["filter[scheduling_status]"] = kwargs["filter_scheduling_status"]
        if kwargs.get("filter_created_since"):
            params["filter[created_since]"] = kwargs["filter_created_since"]
        if kwargs.get("filter_created_until"):
            params["filter[created_until]"] = kwargs["filter_created_until"]
        if kwargs.get("filter_updated_since"):
            params["filter[updated_since]"] = kwargs["filter_updated_since"]
        if kwargs.get("filter_updated_until"):
            params["filter[updated_until]"] = kwargs["filter_updated_until"]
        if kwargs.get("include_sessions") is not None:
            params["include"] = "sessions" if kwargs["include_sessions"] else None
        # page_number is ignored
        data = self._make_request("GET", "events", params)
        if "error" in data:
            return f"Error: {data['error']}"
        complete_data = self._handle_pagination(data, params, "events")
        events_summary = []
        for event in complete_data["data"]:
            title = event["attributes"].get("title", "(no title)")
            event_id = event.get("id", "?")
            status = event["attributes"].get("scheduling_status", "?")
            events_summary.append(f"- {title} (ID: {event_id}, Status: {status})")
        total = len(events_summary)
        all_titles = "\n".join(events_summary)
        return f"FINAL ANSWER: Found {total} events across all pages. Here are all event titles:\n{all_titles}" if total > 0 else "FINAL ANSWER: No events found."

def create_list_events_tool(api_key: str) -> StructuredTool:
    """
    Create the list_events StructuredTool for LangChain
    """
    client = EventsClient(api_key)
    return StructuredTool(
        name="list_events",
        description="""List all events from Livestorm. This tool ALWAYS fetches ALL events across ALL pages, regardless of any page_number input. Do NOT try to paginate or call this tool in a loop. Call it ONCE and it will return a summary of all events. If you want to filter, use the filter parameters. If you want all events, just call it with no filters. Never try to increment page numbers yourself!""",
        args_schema=ListEventsInput,
        func=client.list_events
    ) 