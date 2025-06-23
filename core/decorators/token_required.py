from fastapi import Request, HTTPException
from functools import wraps
from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from common.config import settings

def token_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request")
        if not request:
            raise HTTPException(status_code=400, detail="Request object missing")

        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Authorization token missing")

        if not token.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token format")

        try:
            payload = jwt.decode(
                token.split(" ")[1],
                settings.secret_key,  # Use correct key name
                algorithms=[settings.algorithm]
            )
            request.state.user = payload  # Optionally attach user to request
        except JWTError as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return await func(*args, **kwargs)

    return wrapper