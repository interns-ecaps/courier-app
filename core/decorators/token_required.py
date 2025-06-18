from fastapi.responses import JSONResponse
from jose import JWTError
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from starlette.status import HTTP_401_UNAUTHORIZED
from common.config import Settings
from functools import wraps

settings = Settings()


def token_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or (args[0] if args else None)
        
        if not request:
            return JSONResponse({"error": "Request object missing"}, status_code=400)

        token = request.headers.get("Authorization")
        if not token:
            return JSONResponse(
                {"error": "Authorization token missing"}, status_code=401
            )

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
            request.state.email = payload.get("email")
        except ExpiredSignatureError:
            return JSONResponse({"error": "Token has expired"}, status_code=401)
        except JWTError:
            return JSONResponse({"error": "Invalid token"}, status_code=401)

        return await func(*args, **kwargs)  # Ensure the function is awaited

    return wrapper
