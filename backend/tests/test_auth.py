"""Contract tests for /auth/* endpoints (F10: 用户体系).

Tests cover:
- User registration (POST /auth/register)
- User login (POST /auth/login)
- Current user info (GET /auth/me)
- Token refresh (POST /auth/refresh)
- Logout (POST /auth/logout)
- Session ownership (authenticated vs anonymous sessions)
- Duplicate email / username rejection
- Invalid credentials rejection

Each test uses unique credentials to avoid state leakage through the
persistent database.
"""

import asyncio
import uuid

from run_repository import RunRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_email(prefix="test"):
    """Return a unique email address for test isolation."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _unique_username(prefix="user"):
    """Return a unique username for test isolation."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _register(client, email=None, username=None, password="secret123"):
    """Helper: POST /auth/register and return the response."""
    body = {
        "email": email or _unique_email(),
        "username": username or _unique_username(),
        "password": password,
    }
    return client.post("/auth/register", json=body)


def _login(client, email=None, password="secret123"):
    """Helper: POST /auth/login and return the response."""
    return client.post(
        "/auth/login",
        json={"email": email or _unique_email(), "password": password},
    )


def _register_and_login(client, email=None, username=None, password="secret123"):
    """Helper: register + login, return the access token string."""
    if email is None:
        email = _unique_email()
    if username is None:
        username = _unique_username()
    resp = _register(client, email=email, username=username, password=password)
    assert resp.status_code == 201, f"register failed: {resp.json()}"
    login_resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200, f"login failed: {login_resp.json()}"
    return login_resp.json()["access_token"]


# ---------------------------------------------------------------------------
# /auth/register
# ---------------------------------------------------------------------------


class TestRegister:
    def test_register_creates_user(self, client):
        """POST /auth/register returns 201 with user info."""
        email = _unique_email()
        username = _unique_username()
        resp = _register(client, email=email, username=username)
        assert resp.status_code == 201, f"expected 201, got {resp.status_code}"
        data = resp.json()
        assert data["email"] == email
        assert data["username"] == username
        assert data["is_active"] is True
        assert "id" in data
        assert "uuid" in data
        assert "password" not in data  # never expose the hash
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client):
        """POST /auth/register with existing email returns 409."""
        email = _unique_email()
        username = _unique_username()
        _register(client, email=email, username=username)
        # Try same email, different username
        resp = _register(client, email=email, username=_unique_username())
        assert resp.status_code == 409
        assert "Email already registered" in resp.json()["detail"]

    def test_register_duplicate_username(self, client):
        """POST /auth/register with existing username returns 409."""
        email = _unique_email()
        username = _unique_username()
        _register(client, email=email, username=username)
        # Try different email, same username
        resp = _register(client, email=_unique_email(), username=username)
        assert resp.status_code == 409
        assert "Username already taken" in resp.json()["detail"]

    def test_register_short_password(self, client):
        """POST /auth/register with password < 6 chars returns 422."""
        resp = _register(
            client,
            email=_unique_email(),
            username=_unique_username(),
            password="12345",
        )
        assert resp.status_code == 422

    def test_register_invalid_email(self, client):
        """POST /auth/register with a non-email string returns 422."""
        resp = _register(
            client,
            email=f"not-an-email-{uuid.uuid4().hex[:8]}",
            username=_unique_username(),
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /auth/login
# ---------------------------------------------------------------------------


class TestLogin:
    def test_login_returns_token(self, client):
        """POST /auth/login returns 200 with access_token."""
        email = _unique_email()
        username = _unique_username()
        _register(client, email=email, username=username)
        resp = _login(client, email=email)
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """POST /auth/login with wrong password returns 401."""
        email = _unique_email()
        username = _unique_username()
        _register(client, email=email, username=username)
        resp = _login(client, email=email, password="wrongpass")
        assert resp.status_code == 401

    def test_login_nonexistent_email(self, client):
        """POST /auth/login with unregistered email returns 401."""
        resp = client.post(
            "/auth/login",
            json={"email": _unique_email(), "password": "secret123"},
        )
        assert resp.status_code == 401

    def test_login_empty_password(self, client):
        """POST /auth/login with empty password returns 401 (wrong credentials)."""
        email = _unique_email()
        username = _unique_username()
        _register(client, email=email, username=username)
        resp = client.post(
            "/auth/login",
            json={"email": email, "password": ""},
        )
        # Empty password fails verify_password, returning 401
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /auth/me
# ---------------------------------------------------------------------------


class TestMe:
    def test_me_returns_user(self, client):
        """GET /auth/me returns the authenticated user's profile."""
        email = _unique_email()
        token = _register_and_login(client, email=email)
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == email

    def test_me_no_token(self, client):
        """GET /auth/me without Authorization header returns 401."""
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        """GET /auth/me with a bogus token returns 401."""
        resp = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /auth/refresh
# ---------------------------------------------------------------------------


class TestRefresh:
    def test_refresh_returns_token(self, client):
        """POST /auth/refresh returns a valid access_token."""
        token = _register_and_login(client)
        resp = client.post(
            "/auth/refresh",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        # The new token should be usable to access /auth/me
        me_resp = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {data['access_token']}"},
        )
        assert me_resp.status_code == 200

    def test_refresh_no_token(self, client):
        """POST /auth/refresh without token returns 401."""
        resp = client.post("/auth/refresh")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /auth/logout
# ---------------------------------------------------------------------------


class TestLogout:
    def test_logout_returns_ok(self, client):
        """POST /auth/logout returns 200 with ok: true."""
        token = _register_and_login(client)
        resp = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["ok"] is True

    def test_logout_no_token(self, client):
        """POST /auth/logout without token returns 401."""
        resp = client.post("/auth/logout")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Session ownership
# ---------------------------------------------------------------------------


class TestSessionOwnership:
    def test_production_upload_requires_auth_before_creating_state(
        self, client, sample_csv_path, monkeypatch
    ):
        monkeypatch.setattr("config.settings.DEBUG", False)
        with open(sample_csv_path, "rb") as f:
            response = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={"Idempotency-Key": str(uuid.uuid4())},
            )
        assert response.status_code == 401

    def test_upload_with_auth_creates_owned_session(self, client, sample_csv_path):
        """Authenticated upload creates a session owned by the user."""
        token = _register_and_login(client)
        with open(sample_csv_path, "rb") as f:
            resp = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Idempotency-Key": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 202
        session_id = resp.json()["session_id"]
        # The user should be able to list their own sessions
        sessions_resp = client.get(
            "/sessions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert sessions_resp.status_code == 200
        session_ids = [s["session_id"] for s in sessions_resp.json()]
        assert session_id in session_ids

    def test_owned_session_not_visible_to_other_user(self, client, sample_csv_path):
        """User A's session should not appear in User B's session list."""
        # Register and upload as user A
        token_a = _register_and_login(client)
        with open(sample_csv_path, "rb") as f:
            resp_a = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={
                    "Authorization": f"Bearer {token_a}",
                    "Idempotency-Key": str(uuid.uuid4()),
                },
            )
        assert resp_a.status_code == 202
        session_id_a = resp_a.json()["session_id"]

        # Register as user B
        email_b = _unique_email("user-b")
        username_b = _unique_username("user-b")
        _register(client, email=email_b, username=username_b)
        login_resp = client.post(
            "/auth/login",
            json={"email": email_b, "password": "secret123"},
        )
        assert login_resp.status_code == 200
        token_b = login_resp.json()["access_token"]

        sessions_resp = client.get(
            "/sessions",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert sessions_resp.status_code == 200
        session_ids_b = [s["session_id"] for s in sessions_resp.json()]
        assert session_id_a not in session_ids_b

    def test_upload_resolve_requires_exact_owner_in_production(
        self, client, sample_csv_path, monkeypatch
    ):
        token_a = _register_and_login(client)
        token_b = _register_and_login(client)
        monkeypatch.setattr("config.settings.DEBUG", False)
        key = str(uuid.uuid4())
        with open(sample_csv_path, "rb") as f:
            accepted = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={
                    "Authorization": f"Bearer {token_a}",
                    "Idempotency-Key": key,
                },
            )
        assert accepted.status_code == 202, accepted.text
        owner = client.post(
            "/upload/resolve",
            headers={
                "Authorization": f"Bearer {token_a}",
                "Idempotency-Key": key,
            },
        )
        other = client.post(
            "/upload/resolve",
            headers={
                "Authorization": f"Bearer {token_b}",
                "Idempotency-Key": key,
            },
        )
        missing = client.post(
            "/upload/resolve",
            headers={
                "Authorization": f"Bearer {token_a}",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        assert owner.status_code == 202
        assert owner.json()["run_id"] == accepted.json()["run_id"]
        assert other.status_code == missing.status_code == 404
        assert accepted.json()["session_id"] not in other.text
        assert accepted.json()["run_id"] not in other.text

    def test_anonymous_session_ops_unauthorized_when_debug_false(
        self, client, sample_csv_path, monkeypatch
    ):
        """Anonymous session ops in DEBUG=false return 401."""
        monkeypatch.setattr("config.settings.DEBUG", True)
        with open(sample_csv_path, "rb") as f:
            resp = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={"Idempotency-Key": str(uuid.uuid4())},
            )
        assert resp.status_code == 202
        session_id = resp.json()["session_id"]
        monkeypatch.setattr("config.settings.DEBUG", False)

        info_resp = client.get(f"/sessions/{session_id}")
        assert info_resp.status_code == 401

        eda_resp = client.post(
            f"/sessions/{session_id}/eda", json={"action": "describe"}
        )
        assert eda_resp.status_code == 401

        export_resp = client.get(
            f"/sessions/{session_id}/export", params={"format": "tex"}
        )
        assert export_resp.status_code == 401

    def test_user_b_cannot_operate_on_user_a_session(self, client, sample_csv_path):
        """User B cannot generate-chapter / EDA / export user A's session."""
        token_a = _register_and_login(client)
        token_b = _register_and_login(client)
        with open(sample_csv_path, "rb") as f:
            resp = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={
                    "Authorization": f"Bearer {token_a}",
                    "Idempotency-Key": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 202
        session_id = resp.json()["session_id"]

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        gen = client.post(
            f"/sessions/{session_id}/generate-chapter",
            json={"chapter": {"type": "intro", "title": "引言"}},
            headers=headers_b,
        )
        assert gen.status_code == 403

        eda = client.post(
            f"/sessions/{session_id}/eda",
            json={"action": "describe"},
            headers=headers_b,
        )
        assert eda.status_code == 403

        export = client.get(
            f"/sessions/{session_id}/export",
            params={"format": "tex"},
            headers=headers_b,
        )
        assert export.status_code == 403

        run_id = resp.json()["run_id"]
        assert client.get(f"/runs/{run_id}", headers=headers_b).status_code == 403
        assert (
            client.get(f"/runs/{run_id}/events", headers=headers_b).status_code
            == 403
        )

        # Owner can still read/export their own session.
        own = client.get(f"/sessions/{session_id}", headers=headers_a)
        assert own.status_code == 200

    def test_owned_session_requires_auth_to_delete(self, client, sample_csv_path):
        """Deleting an owned session without auth returns 401."""
        token = _register_and_login(client)
        with open(sample_csv_path, "rb") as f:
            resp = client.post(
                "/upload",
                files={"file": ("sample.csv", f, "text/csv")},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Idempotency-Key": str(uuid.uuid4()),
                },
            )
        assert resp.status_code == 202
        session_id = resp.json()["session_id"]
        run_id = resp.json()["run_id"]

        # Try to delete without auth. The cookie jar holds the login cookies,
        # so drop them to simulate a truly unauthenticated client.
        client.cookies.clear()
        delete_resp = client.delete(f"/sessions/{session_id}")
        assert delete_resp.status_code == 401

        # Delete with auth should succeed (legacy Bearer header still works)
        delete_resp = client.delete(
            f"/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert delete_resp.status_code == 200
        assert asyncio.run(RunRepository().get(run_id)) is None
