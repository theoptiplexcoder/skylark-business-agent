from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.services.monday_service import monday_service
from app.schemas.boards import BoardResponse

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("", response_model=list[BoardResponse])
async def get_boards(user: dict = Depends(get_current_user)):
    boards = await monday_service.get_boards()
    return [
        BoardResponse(
            id=str(b.get("id")),
            name=b.get("name", ""),
            description=b.get("description"),
            columns=b.get("columns"),
        )
        for b in boards
    ]


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(board_id: str, user: dict = Depends(get_current_user)):
    board = await monday_service.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return BoardResponse(
        id=str(board.get("id")),
        name=board.get("name", ""),
        description=board.get("description"),
        columns=board.get("columns"),
    )
