"""
Monday.com Integration using API Token
Handles template uploads to Monday.com boards
"""

import os
import requests
from typing import Dict, Any, Optional

MONDAY_API_URL = "https://api.monday.com/v2"

class MondayIntegration:
    """Monday.com API integration for template uploads"""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize Monday.com integration with API token"""
        self.api_token = api_token or os.getenv('MONDAY_API_TOKEN')
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Monday.com API connection"""
        query = """
        query {
            me {
                id
                name
                email
            }
        }
        """
        
        try:
            response = requests.post(
                MONDAY_API_URL,
                json={"query": query},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                return {
                    "success": False,
                    "error": data["errors"][0]["message"]
                }
            
            return {
                "success": True,
                "user": data["data"]["me"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_boards(self) -> Dict[str, Any]:
        """Get list of user's boards"""
        query = """
        query {
            boards(limit: 50) {
                id
                name
                description
            }
        }
        """
        
        try:
            response = requests.post(
                MONDAY_API_URL,
                json={"query": query},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                return {
                    "success": False,
                    "error": data["errors"][0]["message"]
                }
            
            return {
                "success": True,
                "boards": data["data"]["boards"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_board_from_template(self, template_name: str, template_data: Dict) -> Dict[str, Any]:
        """Create a new Monday.com board from template data"""
        query = """
        mutation ($board_name: String!, $board_kind: BoardKind!) {
            create_board (
                board_name: $board_name,
                board_kind: $board_kind
            ) {
                id
                name
            }
        }
        """
        
        variables = {
            "board_name": template_name,
            "board_kind": "public"
        }
        
        try:
            response = requests.post(
                MONDAY_API_URL,
                json={"query": query, "variables": variables},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                return {
                    "success": False,
                    "error": data["errors"][0]["message"]
                }
            
            board = data["data"]["create_board"]
            
            # Add columns and items from template
            self._populate_board(board["id"], template_data)
            
            return {
                "success": True,
                "board_id": board["id"],
                "board_name": board["name"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _populate_board(self, board_id: str, template_data: Dict):
        """Populate board with template data"""
        # This would parse the template file and add columns/items
        # Implementation depends on template structure
        pass
    
    def upload_template(self, template_file_path: str, template_name: str) -> Dict[str, Any]:
        """
        Upload a template file to Monday.com
        Creates a new board based on the template
        """
        try:
            # Parse template file (Excel, Word, etc.)
            template_data = self._parse_template(template_file_path)
            
            # Create board from template
            result = self.create_board_from_template(template_name, template_data)
            
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_template(self, file_path: str) -> Dict:
        """Parse template file to extract structure"""
        # Basic parser - can be enhanced based on template format
        return {
            "columns": [],
            "items": []
        }


def get_monday_integration(api_token: Optional[str] = None) -> MondayIntegration:
    """Factory function to get Monday.com integration instance"""
    return MondayIntegration(api_token)

