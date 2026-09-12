"""Pilot auth regressions; real DB and routes, no external provider calls."""
import auth
from tests.test_auth_upgrade import _register_and_login, REFRESH


def test_production_anonymous_session_creation_is_denied(client, monkeypatch):
    monkeypatch.setattr('config.settings.DEBUG', False)
    response = client.post('/sessions')
    assert response.status_code == 401


def test_refresh_is_not_a_bearer_access_token(client):
    _register_and_login(client)
    refresh = client.cookies.get(REFRESH)
    response = client.get('/auth/me', headers={'Authorization': f'Bearer {refresh}'})
    assert response.status_code == 401


def test_consumed_refresh_survives_process_memory_loss(client):
    _register_and_login(client)
    refresh = client.cookies.get(REFRESH)
    assert client.post('/auth/refresh').status_code == 200
    # Simulate the old implementation's entire revocation state disappearing.
    if hasattr(auth, '_revoked_jtis'):
        auth._revoked_jtis.clear()
    client.cookies.clear()
    response = client.post('/auth/refresh', headers={'Cookie': f'{REFRESH}={refresh}'})
    assert response.status_code == 401


def test_logged_out_refresh_survives_process_memory_loss(client):
    _register_and_login(client)
    refresh = client.cookies.get(REFRESH)
    assert client.post('/auth/logout').status_code == 200
    if hasattr(auth, '_revoked_jtis'):
        auth._revoked_jtis.clear()
    response = client.post('/auth/refresh', headers={'Cookie': f'{REFRESH}={refresh}'})
    assert response.status_code == 401


async def test_refresh_rejected_by_websocket_token_resolver():
    import pytest
    from fastapi import HTTPException
    token = auth.create_refresh_token({'sub': '1'})
    with pytest.raises(HTTPException) as rejected:
        await auth.get_user_from_token(token, None)
    assert rejected.value.status_code == 401


def test_debug_anonymous_session_creation_remains_available(client):
    assert client.post('/sessions').status_code == 200


async def test_refresh_consumption_is_atomic_across_db_connections(tmp_path):
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.refresh_revocation import RefreshRevocation
    engine = create_async_engine(f'sqlite+aiosqlite:///{tmp_path / "rotation.db"}')
    async with engine.begin() as conn:
        await conn.run_sync(RefreshRevocation.__table__.create)
    sessions = async_sessionmaker(engine)

    async def consume():
        async with sessions() as db:
            accepted = await auth.revoke_jti(db, 'concurrent-single-use-id', 4102444800)
            await db.commit()
            return accepted

    try:
        outcomes = await asyncio.gather(*(consume() for _ in range(6)))
        assert outcomes.count(True) == 1
        assert outcomes.count(False) == 5
    finally:
        await engine.dispose()


def test_revocation_survives_fresh_python_processes(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    program = '''
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.refresh_revocation import RefreshRevocation
from auth import revoke_jti
from config import settings
async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(RefreshRevocation.__table__.create, checkfirst=True)
    async with async_sessionmaker(engine)() as db:
        won = await revoke_jti(db, "restart-ledger-id", 4102444800)
        await db.commit()
        print("accepted" if won else "rejected")
    await engine.dispose()
asyncio.run(main())
'''
    env = {
        'HOME': str(tmp_path), 'DEBUG': 'true',
        'JWT_SECRET_KEY': 'isolated-test-secret-longer-than-32-characters',
        'ECONPAPER_LOCAL_STATE_ROOT': str(tmp_path),
        'DATABASE_URL': f'sqlite+aiosqlite:///{tmp_path / "restart.db"}',
        'PYTHONPATH': os.pathsep.join((str(root), str(root / 'backend'))),
    }
    for expected in ('accepted', 'rejected'):
        process = subprocess.run([sys.executable, '-c', program], env=env,
                                 text=True, capture_output=True, timeout=15)
        assert process.returncode == 0, process.stderr
        assert process.stdout.strip() == expected
