"""Authentication routes: register, login, me, refresh, logout.

F10-hardening: tokens are issued as httpOnly cookies (access + rotating
refresh), login/register are rate-limited, and passwords are checked
against a common-password blacklist. ``Authorization: Bearer`` tokens from
legacy clients stay valid until natural expiry; new tokens are cookie-only,
so the response body no longer carries an access token outside DEBUG
(where it exists for dev/test convenience).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import (
    REFRESH_COOKIE,
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    revoke_jti,
    set_auth_cookies,
    verify_password,
)
from config import settings
from database import get_db
from rate_limit import store as rate_limit_store
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)

    @field_validator("email")
    @classmethod
    def email_must_look_valid(cls, v: str) -> str:
        value = (v or "").strip()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email address")
        local, _, domain = value.partition("@")
        if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("Invalid email address")
        return value


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)


class TokenResponse(BaseModel):
    ok: bool = True
    # DEBUG-only convenience for dev scripts and the pytest suite; always
    # empty in production (cookies are the only transport).
    access_token: str = ""
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    uuid: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LogoutResponse(BaseModel):
    ok: bool = True


# ---------------------------------------------------------------------------
# Password policy (NIST 800-63B: length over composition rules)
# ---------------------------------------------------------------------------

# Top of the common-password corpus (SecLists top-300 subset, lowercased).
# A shared-password check catches the bulk of real-world credential stuffing
# without pulling in a heavy library.
_COMMON_PASSWORDS = frozenset(
    """password 123456 123456789 12345678 12345 qwerty abc123 password1 111111
    1234567 dragon 123123 qwertyuiop 000000 123321 654321 iloveyou 121212
    abc123456 a123456 qwe123 1q2w3e4r 123qwe monkey 1234567890 letmein
    admin welcome passwd login passw0rd password123 azerty superman batman
    sunshine football baseball master shadow michael jennifer charlie
    trustno1 hunter freedom whatever starwars princess cheese daniel
    jordan23 harley 156981 asdfgh zxcvbn 1qaz2wsx qazwsx pokemon google
    asdf1234 samsung matrix murphy cooper fisher morgan richard philip
    chelsea andrew joshua maggie thomas robert daniel tigger pepper
""".split()
)


def validate_password_strength(password: str) -> None:
    """Raise 422 unless the password meets the minimum policy."""
    problems: list[str] = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if password.strip().lower() in _COMMON_PASSWORDS:
        problems.append("too common")
    if len(set(password)) == 1:
        problems.append("not a single repeated character")
    if problems:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password needs: " + ", ".join(problems),
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> User:
    """Register a new user account.

    Raises 409 if the email or username is already taken. When
    ``HIDE_REGISTRATION_EXISTENCE`` is enabled (with the email-verification
    flow, later ticket), duplicates get a generic 201 instead so the
    endpoint cannot be used to enumerate accounts.
    """
    validate_password_strength(body.password)

    result = await db.execute(select(User).where(User.email == body.email))
    email_taken = result.scalar_one_or_none() is not None
    result = await db.execute(select(User).where(User.username == body.username))
    username_taken = result.scalar_one_or_none() is not None

    if (email_taken or username_taken) and settings.HIDE_REGISTRATION_EXISTENCE:
        # Enumeration guard: pretend success. Real delivery requires the
        # email-verification flow — placeholder until then.
        return User(
            id=0,
            uuid="",
            email=body.email,
            username=body.username,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )

    if email_taken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    if username_taken:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Authenticate a user and set the httpOnly cookie pair.

    Guarded twice: per-IP window (production) and per-account lockout
    (5 consecutive failures → 10 min). Failure messages never distinguish
    "no such email" from "wrong password".
    """
    rate_limit_store.assert_ip_allowed(request.client.host if request.client else "unknown")
    rate_limit_store.assert_not_locked(body.email)

    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        rate_limit_store.record_failure(body.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    rate_limit_store.record_success(body.email)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    set_auth_cookies(response, access_token, refresh_token)
    return {
        "ok": True,
        "access_token": access_token if settings.DEBUG else "",
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rotate the refresh cookie and mint a fresh access token.

    Strictly cookie-based: the old refresh token is revoked (single use),
    so a stolen refresh token dies on first legitimate rotation. Legacy
    Bearer-only clients get 401 and simply log in again.
    """
    raw = request.cookies.get(REFRESH_COOKIE)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            raw,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    if payload.get("typ") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    jti = payload.get("jti") or ""
    from auth import is_jti_revoked

    if jti and is_jti_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Rotate: the presented refresh token must never work again.
    exp = payload.get("exp")
    if jti and exp:
        revoke_jti(jti, float(exp))

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    set_auth_cookies(response, access_token, refresh_token)
    return {
        "ok": True,
        "access_token": access_token if settings.DEBUG else "",
        "token_type": "bearer",
    }


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Log out: revoke the presented refresh token and clear cookies.

    The access cookie dies here and now; any other tab holds at most a
    15-minute access token, after which the revoked refresh cannot renew.
    """
    raw = request.cookies.get(REFRESH_COOKIE)
    if raw:
        try:
            payload = jwt.decode(
                raw,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                revoke_jti(str(jti), float(exp))
        except JWTError:
            pass  # already-expired refresh: clearing cookies is enough
    clear_auth_cookies(response)
    return {"ok": True}
