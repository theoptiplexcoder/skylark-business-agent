from fastapi import APIRouter, HTTPException, Response, Depends
from app.services.auth_service import auth_service
from app.core.dependencies import get_current_user
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    theme_preference: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str = "viewer"
    avatar_url: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    theme_preference: str = "dark"


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: RegisterRequest, response: Response):
    try:
        result = auth_service.signup(body.email, body.password, body.name)

        if result.get("access_token"):
            response.set_cookie(
                "access_token", result["access_token"],
                httponly=True, secure=True, samesite="lax", max_age=604800,
            )
            response.set_cookie(
                "refresh_token", result["refresh_token"],
                httponly=True, secure=True, samesite="lax", max_age=604800,
            )

        return TokenResponse(
            access_token=result["access_token"] or "",
            refresh_token=result["refresh_token"] or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response):
    try:
        result = auth_service.login(body.email, body.password)

        response.set_cookie(
            "access_token", result["access_token"],
            httponly=True, secure=True, samesite="lax",
            max_age=604800 if body.remember_me else 1800,
        )
        response.set_cookie(
            "refresh_token", result["refresh_token"],
            httponly=True, secure=True, samesite="lax", max_age=604800,
        )

        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/logout")
async def logout(response: Response, user: dict = Depends(get_current_user)):
    auth_service.logout(user.get("id", ""))
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest):
    try:
        result = auth_service.refresh_token(body.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(**user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(body: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    try:
        update_data = body.model_dump(exclude_unset=True)
        updated = auth_service.update_profile(user["id"], **update_data)
        return UserResponse(**updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
