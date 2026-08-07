from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.core.supabase import supabase, supabase_admin
from app.core.logging import logger

security = HTTPBearer(auto_error=False)


class AuthService:
    """Supabase Auth integration."""

    def __init__(self, client: Client = None):
        self.client = client or supabase

    def signup(self, email: str, password: str, name: str) -> dict:
        try:
            result = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {"data": {"name": name}},
            })
            if result.user is None:
                raise ValueError("Signup failed")
            logger.info("User signed up: %s", email)
            return {
                "user": {
                    "id": result.user.id,
                    "email": result.user.email,
                    "name": name,
                },
                "access_token": result.session.access_token if result.session else None,
                "refresh_token": result.session.refresh_token if result.session else None,
            }
        except Exception as e:
            error_msg = str(e)
            if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
                raise ValueError("Email already registered")
            raise ValueError(f"Signup failed: {error_msg}")

    def login(self, email: str, password: str) -> dict:
        try:
            result = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            if result.user is None:
                raise ValueError("Invalid credentials")
            logger.info("User logged in: %s", email)
            return {
                "user": {
                    "id": result.user.id,
                    "email": result.user.email,
                    "name": result.user.user_metadata.get("name", ""),
                },
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token,
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Login failed: {str(e)}")

    def logout(self, access_token: str) -> None:
        try:
            self.client.auth.sign_out()
            logger.info("User logged out")
        except Exception as e:
            logger.warning("Logout error: %s", e)

    def refresh_token(self, refresh_token: str) -> dict:
        try:
            result = self.client.auth.refresh_session(refresh_token)
            if result.session is None:
                raise ValueError("Refresh failed")
            return {
                "access_token": result.session.access_token,
                "refresh_token": result.session.refresh_token,
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Token refresh failed: {str(e)}")

    def get_user(self, access_token: str) -> dict:
        try:
            result = self.client.auth.get_user(access_token)
            if result.user is None:
                raise ValueError("User not found")
            return {
                "id": result.user.id,
                "email": result.user.email,
                "name": result.user.user_metadata.get("name", ""),
                "role": result.user.user_metadata.get("role", "viewer"),
                "avatar_url": result.user.user_metadata.get("avatar_url"),
                "company": result.user.user_metadata.get("company"),
                "job_title": result.user.user_metadata.get("job_title"),
                "theme_preference": result.user.user_metadata.get("theme_preference", "dark"),
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to get user: {str(e)}")

    def update_profile(self, access_token: str, **kwargs) -> dict:
        try:
            result = self.client.auth.update_user(access_token, {"data": kwargs})
            if result.user is None:
                raise ValueError("Update failed")
            return self.get_user(access_token)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Profile update failed: {str(e)}")


auth_service = AuthService()
