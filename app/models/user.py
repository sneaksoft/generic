from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """User model supporting both local (email/password) and OAuth authentication.

    For local users: email + hashed_password are set; oauth_* fields are None.
    For OAuth users: email + oauth_provider_* fields are set; hashed_password is None.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Local authentication (email + password)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # OAuth authentication
    oauth_provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    oauth_provider_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    oauth_access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    oauth_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        auth_type = "oauth" if self.oauth_provider_name else "local"
        return f"<User id={self.id} email={self.email!r} auth={auth_type}>"
