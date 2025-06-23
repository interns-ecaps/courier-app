# courier_app/core/decorators/token_required.py

from fastapi.responses import JSONResponse
from fastapi import Request
from jose import JWTError
import jwt
from jwt import ExpiredSignatureError
from starlette.status import HTTP_401_UNAUTHORIZED
from functools import wraps
from common.config import Settings

settings = Settings()

def token_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or (args[0] if args else None)

        if not request:
            return JSONResponse({"error": "Request object missing"}, status_code=400)

        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return JSONResponse({"error": "Authorization token missing"}, status_code=HTTP_401_UNAUTHORIZED)

        try:
            payload = jwt.decode(token.split(" ")[1], settings.jwt_secret_key, algorithms=["HS256"])
            request.state.email = payload.get("email")
        except ExpiredSignatureError:
            return JSONResponse({"error": "Token expired"}, status_code=HTTP_401_UNAUTHORIZED)
        except JWTError:
            return JSONResponse({"error": "Invalid token"}, status_code=HTTP_401_UNAUTHORIZED)

        return await func(*args, **kwargs)

    return wrapper
