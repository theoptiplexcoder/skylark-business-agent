import asyncio
from typing import Dict, List, Any, Optional
from app.services.schema_service import schema_service
from app.core.logging import logger

class MetadataService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._last_fetched: float = 0
        self._lock = asyncio.Lock()
        self.CACHE_TTL = 3600  # Cache for 1 hour

    async def get_all_boards(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get all board metadata, using cache if available."""
        loop = asyncio.get_running_loop()
        current_time = loop.time()
        
        async with self._lock:
            if force_refresh or not self._cache or (current_time - self._last_fetched > self.CACHE_TTL):
                logger.info("Cache miss. Fetching fresh schema.")
                boards = await schema_service.get_all_boards_schema()
                self._cache = {b["id"]: b for b in boards}
                self._last_fetched = current_time
            else:
                logger.debug("Cache hit for board schema.")
        
        return list(self._cache.values())

    async def get_board(self, board_id: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific board."""
        await self.get_all_boards() # ensure cache is warm
        return self._cache.get(board_id)

metadata_service = MetadataService()
