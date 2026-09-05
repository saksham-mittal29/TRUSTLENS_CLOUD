from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    firebase_uid: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    verifications: Mapped[list["Verification"]] = relationship(
        back_populates="user"
    )


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    original_response: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    trust_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    total_claims: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    supported_claims: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    contradicted_claims: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    uncertain_claims: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user: Mapped["User | None"] = relationship(
        back_populates="verifications"
    )

    claims: Mapped[list["Claim"]] = relationship(
        back_populates="verification",
        cascade="all, delete-orphan"
    )


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    verification_id: Mapped[int] = mapped_column(
        ForeignKey("verifications.id"),
        nullable=False
    )

    claim_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    verdict: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    confidence: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    evidence_quality: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    verification: Mapped["Verification"] = relationship(
        back_populates="claims"
    )
