"""Persistent single-use refresh-token ledger (no raw credentials)."""
from sqlalchemy import Column, Float, String
from database import Base


class RefreshRevocation(Base):
    __tablename__ = "refresh_revocations"

    jti = Column(String(64), primary_key=True)
    expires_at = Column(Float, nullable=False, index=True)
