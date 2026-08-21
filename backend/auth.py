"""Authentication utilities: password hashing, JWT, and dependency injection.

Uses passlib (bcrypt) for password hashing and python-jose for JWT tokens.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.user import User

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT token management
# ---------------------------------------------------------------------------

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    The token payload includes the ``data`` dict plus ``exp`` and ``iat``.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Raises ``HTTPException(401)`` if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------


async def get_current_user(
    token: Optional[str] = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency: resolve the current user from the Authorization header.

    Returns the ``User`` ORM instance. Raises ``HTTPException(401)`` when
    the token is missing, invalid, or the user does not exist.

    When *no* token is provided, raises 401 so that protected endpoints
    require authentication. Use ``Optional[User]`` via ``get_optional_user``
    for endpoints that work both authenticated and anonymously.
    """
    return await _resolve_user(token, db, required=True)


async def get_optional_user(
    token: Optional[str] = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """FastAPI dependency: like ``get_current_user`` but returns ``None``
    when no token is provided (instead of raising 401)."""
    return await _resolve_user(token, db, required=False)


async def get_user_from_token(
    token: Optional[str],
    db: AsyncSession,
) -> Optional[User]:
    """Resolve a user from a raw token string (WebSocket query / subprotocol)."""
    return await _resolve_user(token, db, required=False)


async def _resolve_user(
    token: Optional[str],
    db: AsyncSession,
    required: bool,
) -> Optional[User]:
    """Shared logic for resolving a user from an optional token."""
    if not token:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return None

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return None

    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()
    if user is None:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return None
    return user


# ---------------------------------------------------------------------------
# Session ownership + debug-gated auth
# ---------------------------------------------------------------------------


def require_session_ownership(session_id: str, user: Optional[User]) -> None:
    """Enforce session existence and ownership on session-scoped routes.

    - Session missing → 404
    - Session has owner_id → require authenticated user and user.id == owner_id
      (401 if unauthenticated, 403 if a different user)
    - Session has no owner (anonymous) AND DEBUG is false → 401
    - Session has no owner AND DEBUG is true → allow (local demo)
    """
    from facade import facade

    if not facade.has_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    owner_id = facade.get_session_owner(session_id)
    if owner_id is not None:
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for this session",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own this session",
            )
        return

    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this session",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_auth_unless_debug(user: Optional[User]) -> None:
    """Require an authenticated user when DEBUG is false (desk / demo routes)."""
    if user is None and not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
