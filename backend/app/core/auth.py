from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .firebase import firebase_service

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.firebase = firebase_service
        
    async def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """
        Verify Firebase ID token and return user information
        """
        try:
            # Initialize Firebase if not already done
            if self.firebase._app is None:
                self.firebase.initialize()
            
            # Verify the token
            decoded_token = self.firebase.verify_token(credentials.credentials)
            
            if decoded_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return {
                "uid": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "email_verified": decoded_token.get("email_verified", False)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Global auth service instance
auth_service = AuthService()

# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    return await auth_service.get_current_user(credentials)

# Optional authentication dependency
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    if credentials is None:
        return None
    return await auth_service.get_current_user(credentials)