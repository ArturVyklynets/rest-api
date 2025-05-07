from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import TokenResponse, RefreshTokenRequest
from .security import create_access_token, create_refresh_token, verify_user

auth_router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 8
REFRESH_TOKEN_EXPIRE_DAYS = 5


@auth_router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_user(form_data.username, form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": form_data.username},
                                       expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(data={"sub": form_data.username},
                                         expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    try:
        username = verify_user(token=request.refresh_token, refresh=True)
        new_access_token = create_access_token(data={"sub": username},
                                               expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return TokenResponse(access_token=new_access_token, refresh_token=request.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
