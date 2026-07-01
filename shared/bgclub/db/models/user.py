import enum

from datetime import datetime



from sqlalchemy import BigInteger, DateTime, Enum, String, func

from sqlalchemy.orm import Mapped, mapped_column



from bgclub.db.base import Base





class UserRole(str, enum.Enum):

    guest = "guest"

    admin = "admin"





class UserLanguage(str, enum.Enum):

    ru = "ru"

    en = "en"

    ua = "ua"





class UserTheme(str, enum.Enum):

    synthwave = "synthwave"

    midnight = "midnight"

    aurora = "aurora"

    daylight = "daylight"





class User(Base):

    __tablename__ = "users"



    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role: Mapped[UserRole] = mapped_column(

        Enum(UserRole, name="user_role"),

        default=UserRole.guest,

        server_default=UserRole.guest.value,

    )

    language: Mapped[UserLanguage | None] = mapped_column(

        Enum(UserLanguage, name="user_language"),

        nullable=True,

    )

    theme: Mapped[UserTheme | None] = mapped_column(

        Enum(UserTheme, name="user_theme"),

        nullable=True,

    )

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        server_default=func.now(),

    )

    updated_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        server_default=func.now(),

        onupdate=func.now(),

    )


