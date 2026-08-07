"""FastAPI routes for Monday.com data."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.services.monday import (
    dashboards as dashboards_service,
    boards as boards_service,
    users as users_service,
    workspaces as workspaces_service,
)
from app.services.monday.exceptions import MondayAPIError

router = APIRouter(prefix="/monday", tags=["monday"])


# ── Dashboards ─────────────────────────────────────────────

@router.get("/dashboards")
async def list_dashboards():
    try:
        dashboards = await dashboards_service.get_dashboards()
        return {"dashboards": dashboards, "count": len(dashboards)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    try:
        result = await dashboards_service.get_dashboard_complete(dashboard_id)
        return result
    except MondayAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=502, detail=str(e))


# ── Boards ─────────────────────────────────────────────────

@router.get("/boards")
async def list_boards():
    try:
        boards = await boards_service.get_boards()
        return {"boards": boards, "count": len(boards)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/board/{board_id}")
async def get_board(board_id: str):
    try:
        board = await boards_service.get_board_by_id(board_id)
        return board
    except MondayAPIError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/board/{board_id}/groups")
async def list_groups(board_id: str):
    try:
        groups = await boards_service.get_groups(board_id)
        return {"groups": groups, "count": len(groups)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/board/{board_id}/columns")
async def list_columns(board_id: str):
    try:
        columns = await boards_service.get_columns(board_id)
        return {"columns": columns, "count": len(columns)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/board/{board_id}/updates")
async def list_recent_updates(board_id: str, limit: int = Query(20, ge=1, le=100)):
    try:
        updates = await boards_service.get_recent_updates(board_id, limit=limit)
        return {"updates": updates, "count": len(updates)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Items ──────────────────────────────────────────────────

@router.get("/items/{board_id}")
async def list_items(
    board_id: str,
    limit: int = Query(100, ge=1, le=500),
    group_id: Optional[str] = None,
):
    try:
        result = await boards_service.get_items(board_id, limit=limit, group_id=group_id)
        return {"items": result["items"], "cursor": result.get("cursor"), "count": len(result["items"])}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/items/{board_id}/all")
async def list_all_items(board_id: str, max_items: int = Query(2000, ge=1, le=5000)):
    try:
        items = await boards_service.get_all_items(board_id, max_items=max_items)
        return {"items": items, "count": len(items)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/item/{item_id}/subitems")
async def list_subitems(item_id: str):
    try:
        subitems = await boards_service.get_subitems(item_id)
        return {"subitems": subitems, "count": len(subitems)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/item/{item_id}/updates")
async def list_item_updates(item_id: str, limit: int = Query(50, ge=1, le=100)):
    try:
        updates = await boards_service.get_updates(item_id, limit=limit)
        return {"updates": updates, "count": len(updates)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Users & Teams ──────────────────────────────────────────

@router.get("/users")
async def list_users():
    try:
        users = await users_service.get_users()
        return {"users": users, "count": len(users)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/user/{user_id}")
async def get_user(user_id: str):
    try:
        user = await users_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/teams")
async def list_teams():
    try:
        teams = await users_service.get_teams()
        return {"teams": teams, "count": len(teams)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Workspaces ─────────────────────────────────────────────

@router.get("/workspaces")
async def list_workspaces():
    try:
        workspaces = await workspaces_service.get_workspaces()
        return {"workspaces": workspaces, "count": len(workspaces)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/workspace/{workspace_id}")
async def get_workspace(workspace_id: str):
    try:
        workspace = await workspaces_service.get_workspace_by_id(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/folders")
async def list_folders(workspace_id: Optional[str] = None):
    try:
        folders = await workspaces_service.get_folders(workspace_id=workspace_id)
        return {"folders": folders, "count": len(folders)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/board/{board_id}/connected")
async def list_connected_boards(board_id: str):
    try:
        connected = await workspaces_service.get_connected_boards(board_id)
        return {"connected_boards": connected, "count": len(connected)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── Tags ───────────────────────────────────────────────────

@router.get("/tags")
async def list_tags():
    try:
        tags = await boards_service.get_tags()
        return {"tags": tags, "count": len(tags)}
    except MondayAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
