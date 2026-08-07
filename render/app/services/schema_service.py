import json
from typing import Dict, List, Any
from app.services.monday_service import monday_service
from app.core.logging import logger

class SchemaService:
    async def get_all_boards_schema(self) -> List[Dict[str, Any]]:
        """Retrieves schema for all boards to be cached."""
        logger.info("Fetching schema for all boards.")
        boards = await monday_service.get_boards()
        
        schema = []
        for board in boards:
            schema.append({
                "id": board["id"],
                "name": board["name"],
                "description": board.get("description", ""),
                "columns": board.get("columns", [])
            })
        return schema
        
    async def get_board_schema(self, board_id: str) -> Dict[str, Any]:
        """Fetch schema for a specific board."""
        return await monday_service.get_board(board_id)

schema_service = SchemaService()
