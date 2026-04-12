from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.schemas.common import DocumentStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    application_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    document_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=DocumentStatus.UPLOADED.value,
        nullable=False,
    )
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
    )

    application: Mapped["Application"] = relationship("Application", back_populates="documents")
    pages: Mapped[list["DocumentPage"]] = relationship(
        "DocumentPage",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="DocumentPage.page_number",
    )
    validation_flags: Mapped[list["ValidationFlag"]] = relationship(
        "ValidationFlag",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="ValidationFlag.created_at",
    )
    extracted_fields: Mapped[list["ExtractedField"]] = relationship(
        "ExtractedField",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="ExtractedField.created_at",
    )
    review_actions: Mapped[list["ReviewAction"]] = relationship(
        "ReviewAction",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="ReviewAction.created_at",
    )

    @property
    def validation_flag_count(self) -> int:
        return len(self.validation_flags)
