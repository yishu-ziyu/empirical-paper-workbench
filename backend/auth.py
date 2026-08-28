"""Authentication utilities: password hashing, JWT, and dependency injection.

Uses bcrypt for password hashing and python-jose for JWT tokens.

Token transport (F10-hardening): access + refresh tokens are issued as
``httpOnly`` cookies so XSS cannot read them. The ``Authorization: Bearer``
header is still accepted for legacy clients during the compat window, but
new clients must rely on cookies. Refresh tokens are single-use (rotated on
every /auth/refresh) and revocable via an in-process jti denylist.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.user import User

ACCESS_COOKIE = "ep_access"
REFRESH_COOKIE = "ep_access_refresh"
REFRESH_PATH = "/auth"

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

# bcrypt 算法本身只加密前 72 字节(passlib 时代静默截断)。bcrypt 5.x 起
# 对超长输入直接抛错，这里手动截断，保持与既有 $2b$ 哈希可互相验证。
_BCRYPT_MAX_SECRET_BYTES = 72


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    secret = password.encode("utf-8")[:_BCRYPT_MAX_SECRET_BYTES]
    return bcrypt.hashpw(secret, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    secret = plain_password.encode("utf-8")[:_BCRYPT_MAX_SECRET_BYTES]
    try:
        return bcrypt.checkpw(secret, hashed_password.encode("utf-8"))
    except ValueError:
        # 非法哈希串按"密码不匹配"处理，而不是让请求 500。
        return False


# ---------------------------------------------------------------------------
# JWT token management
# ---------------------------------------------------------------------------

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token.

    The token payload includes the ``data`` dict plus ``typ``, ``jti``,
    ``exp`` and ``iat``.
    """
    return _create_token(data, expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), typ="access")


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT refresh token (long-lived, single-use via rotation)."""
    return _create_token(
        data,
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        typ="refresh",
    )


def _create_token(data: dict, expires_delta: timedelta, typ: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update(
        {
            "typ": typ,
            "jti": uuid.uuid4().hex,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
    )
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


# ---------------------------------------------------------------------------
# Refresh-token denylist (logout / rotation revocation)
# ---------------------------------------------------------------------------

_revoked_lock = threading.Lock()
_revoked_jtis: dict[str, float] = {}  # jti -> epoch exp


def revoke_jti(jti: str, exp: float) -> None:
    """Add a token id to the denylist until its natural expiry."""
    with _revoked_lock:
        _revoked_jtis[jti] = exp
        # prune anything already past its expiry
        now = datetime.now(timezone.utc).timestamp()
        for k in [k for k, v in _revoked_jtis.items() if v < now]:
            _revoked_jtis.pop(k, None)


def is_jti_revoked(jti: str) -> bool:
    return jti in _revoked_jtis


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token.

    Raises ``HTTPException(401)`` if the token is invalid or expired.
    """
    return _decode(token, expected_typ=None)


def _decode(token: str, expected_typ: Optional[str]) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if expected_typ is not None and payload.get("typ") not in (None, expected_typ):
        # ``None`` keeps legacy no-typ tokens valid during the compat window.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    if payload.get("jti") and is_jti_revoked(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    return payload


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency: resolve the current user.

    Token source order: ``Authorization: Bearer`` header (legacy compat),
    then the ``ep_access`` httpOnly cookie. Cookie tokens must be
    ``typ=access`` strictly; header tokens may omit ``typ`` (legacy).

    Raises 401 when no valid token. Use ``get_optional_user`` for endpoints
    that work both authenticated and anonymously.
    """
    return await _resolve_user(request, token, db, required=True)


async def get_optional_user(
    request: Request,
    token: Optional[str] = Depends(_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """FastAPI dependency: like ``get_current_user`` but returns ``None``
    when no token is provided (instead of raising 401)."""
    return await _resolve_user(request, token, db, required=False)


async def get_user_from_token(
    token: Optional[str],
    db: AsyncSession,
) -> Optional[User]:
    """Resolve a user from a raw token string (WebSocket query / subprotocol)."""
    return await _resolve_user(None, token, db, required=False)


async def _resolve_user(
    request: Optional[Request],
    header_token: Optional[str],
    db: AsyncSession,
    required: bool,
) -> Optional[User]:
    """Shared logic for resolving a user from header or cookie token."""
    token = header_token
    from_cookie = False
    if not token and request is not None:
        token = request.cookies.get(ACCESS_COOKIE)
        from_cookie = True
    if not token:
        if required:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None

    payload = _decode(token, expected_typ="access" if from_cookie else None)
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
# Cookie helpers
# ---------------------------------------------------------------------------


def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    """Attach httpOnly auth cookies.

    ``secure`` follows the deployment: on (production, DEBUG=false), off for
    local http. SameSite=Lax keeps cross-site POSTs from carrying the cookie;
    the frontend is same-origin (Vite proxy / nginx) so this costs nothing.
    The refresh cookie is scoped to /auth so it is not sent with every
    API request.
    """
    secure = not settings.DEBUG
    response.set_cookie(
        ACCESS_COOKIE,
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=secure,
        samesite="lax",
        path=REFRESH_PATH,
    )


def clear_auth_cookies(response) -> None:
    """Delete both auth cookies (logout)."""
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_PATH)


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
