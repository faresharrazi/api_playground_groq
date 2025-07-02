"""
Base Livestorm API client for shared functionality
"""

import requests
from typing import Dict, Any, Optional


class LivestormBaseClient:
    """Base client for Livestorm API operations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.livestorm.co/v1"
        self.headers = {
            "accept": "application/vnd.api+json",
            "Authorization": api_key
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Livestorm API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _handle_pagination(self, data: Dict[str, Any], params: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """
        Handle pagination for API responses
        
        Args:
            data: Initial API response
            params: Original request parameters
            endpoint: The API endpoint being called
            
        Returns:
            Complete data with all pages merged
        """
        all_data = data.get("data", [])
        meta = data.get("meta", {})
        
        # If there are more pages, fetch them all
        if meta.get("page_count", 1) > 1:
            current_page = meta.get("current_page", 0)
            page_count = meta.get("page_count", 1)
            
            for page in range(current_page + 1, page_count):
                page_params = params.copy()
                page_params["page[number]"] = str(page)
                
                page_response = self._make_request("GET", endpoint, page_params)
                if "error" not in page_response:
                    all_data.extend(page_response.get("data", []))
        
        return {
            "data": all_data,
            "meta": meta
        } 