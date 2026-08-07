from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict | None:
    if credentials is None:
        return None

    token = credentials.credentials
    service = AuthService()
    try:
        user = service.get_user(token)
        return user
    except ValueError:
        return None
