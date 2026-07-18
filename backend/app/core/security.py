from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid
import bcrypt
import jwt
from app.core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

bearer_scheme = HTTPBearer()

token_blacklist: set[str] = set()


def revoke_token(jti: str) -> None:
    token_blacklist.add(jti)


def is_token_revoked(jti: str) -> bool:
    return jti in token_blacklist


def get_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    return credentials.credentials


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            hours=settings.ACCESS_TOKEN_EXPIRE_HOURS
        )
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None