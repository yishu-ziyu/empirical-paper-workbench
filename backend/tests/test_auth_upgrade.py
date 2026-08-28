"""F10-hardening tests: cookie transport, rotation, revocation, lockout.

Covers the auth-upgrade contract that test_auth.py predates:
- login sets httpOnly access+refresh cookies (refresh scoped to /auth)
- requests authenticate via cookies alone (no Authorization header)
- /auth/refresh rotates: the presented refresh token is single-use
- logout revokes the refresh token (replay → 401)
- refresh tokens cannot authenticate as access tokens (typ check)
- 5 consecutive login failures lock the account for 10 minutes
- weak / common passwords are rejected at registration
- production login responses carry no token in the body
"""

import uuid

from tests.test_auth import _register, _unique_email, _unique_username

ACCESS = "ep_access"
REFRESH = "ep_access_refresh"


def _register_and_login(client, password="correct horse battery staple"):
    email = _unique_email()
    username = _unique_username()
    resp = _register(client, email=email, username=username, password=password)
    assert resp.status_code == 201, resp.json()
    login = client.post("/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.json()
    return email, login


class TestCookieTransport:
    def test_login_sets_httponly_cookies(self, client):
        """Both cookies are HttpOnly; refresh is scoped to /auth."""
        _, login = _register_and_login(client)
        set_cookies = login.headers.get_list("set-cookie")
        access_raw = [c for c in set_cookies if c.startswith(ACCESS + "=")]
        refresh_raw = [c for c in set_cookies if c.startswith(REFRESH + "=")]
        assert access_raw and refresh_raw
        assert "httponly" in access_raw[0].lower()
        assert "httponly" in refresh_raw[0].lower()
        assert "path=/auth" in refresh_raw[0].lower()
        assert "samesite=lax" in access_raw[0].lower()

    def test_cookie_alone_authenticates(self, client):
        """GET /auth/me with zero Authorization headers, cookies only."""
        email, _ = _register_and_login(client)
        resp = client.get("/auth/me")
        assert resp.status_code == 200, resp.text
        assert resp.json()["email"] == email

    def test_refresh_cookie_cannot_authenticate_me(self, client):
        """A refresh token presented as the access cookie must be rejected."""
        _register_and_login(client)
        refresh_value = client.cookies.get(REFRESH)
        client.cookies.set(ACCESS, refresh_value)
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_production_login_body_carries_no_token(self, client, monkeypatch):
        """Outside DEBUG the token exists only in cookies, never the body."""
        monkeypatch.setattr("config.settings.DEBUG", False)
        _, login = _register_and_login(client)
        assert login.json()["access_token"] == ""
        assert client.cookies.get(ACCESS)


class TestRotation:
    def test_refresh_rotates_and_old_token_dies(self, client):
        """Presented refresh token is single-use: replay returns 401."""
        _register_and_login(client)
        old_refresh = client.cookies.get(REFRESH)

        first = client.post("/auth/refresh")
        assert first.status_code == 200, first.text
        assert client.cookies.get(REFRESH) != old_refresh

        # Replay the pre-rotation refresh token: must be revoked.
        client.cookies.set(REFRESH, old_refresh)
        replay = client.post("/auth/refresh")
        assert replay.status_code == 401

    def test_rotated_access_token_works(self, client):
        """After rotation the new access cookie authenticates immediately."""
        _register_and_login(client)
        resp = client.post("/auth/refresh")
        assert resp.status_code == 200
        me = client.get("/auth/me")
        assert me.status_code == 200

    def test_refresh_without_cookie_returns_401(self, client):
        resp = client.post("/auth/refresh")
        assert resp.status_code == 401


class TestRevocation:
    def test_logout_revokes_refresh_and_clears_cookies(self, client):
        """After logout the refresh token replay is rejected."""
        _register_and_login(client)
        refresh_value = client.cookies.get(REFRESH)

        out = client.post("/auth/logout")
        assert out.status_code == 200
        assert out.json()["ok"] is True
        assert client.cookies.get(ACCESS) is None

        # Replay the revoked refresh token.
        client.cookies.set(REFRESH, refresh_value)
        replay = client.post("/auth/refresh")
        assert replay.status_code == 401

    def test_logout_without_cookies_still_ok(self, client):
        """Header-only legacy logout stays a 200 no-op."""
        email, login = _register_and_login(client)
        token = login.json()["access_token"]
        client.cookies.clear()
        resp = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


class TestLockout:
    def test_five_failures_lock_account(self, client):
        """5 consecutive failures → even the correct password is locked out."""
        email, _ = _register_and_login(
            client, password="staple-morse-vendor-9"
        )
        for _ in range(5):
            bad = client.post(
                "/auth/login",
                json={"email": email, "password": "totally-wrong"},
            )
            assert bad.status_code == 401

        locked = client.post(
            "/auth/login",
            json={"email": email, "password": "staple-morse-vendor-9"},
        )
        assert locked.status_code == 423


class TestPasswordPolicy:
    def test_common_password_rejected(self, client):
        resp = _register(
            client,
            email=_unique_email(),
            username=_unique_username(),
            password="password123",
        )
        assert resp.status_code == 422
        assert "too common" in resp.json()["detail"]

    def test_short_password_rejected(self, client):
        resp = _register(
            client,
            email=_unique_email(),
            username=_unique_username(),
            password="a1b2c3d",
        )
        assert resp.status_code == 422

    def test_strong_passphrase_accepted(self, client):
        email = _unique_email()
        resp = _register(
            client,
            email=email,
            username=_unique_username(),
            password="correct horse battery staple",
        )
        assert resp.status_code == 201, resp.json()
