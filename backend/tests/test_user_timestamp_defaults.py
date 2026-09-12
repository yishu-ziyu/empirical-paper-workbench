"""User values must fit the existing PostgreSQL TIMESTAMP WITHOUT TIME ZONE columns."""
from datetime import datetime, timezone

import pytest

from models.user import User


@pytest.mark.parametrize('column_name,operation', [
    ('created_at', 'default'),
    ('updated_at', 'default'),
    ('updated_at', 'onupdate'),
])
def test_user_timestamp_is_naive_utc_for_existing_schema(column_name, operation):
    column = User.__table__.columns[column_name]
    assert column.type.timezone is False
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    generated = getattr(column, operation).arg(None)
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    assert generated.tzinfo is None
    assert before <= generated <= after
