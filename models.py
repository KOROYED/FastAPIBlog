from __future__ import annotations                                                          # for forward reference

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    posts: Mapped[list[Post]] = relationship(
        back_populates="author", 
        cascade="all, delete-orphan",                                                       # if user is deleted, delete all of their posts too
    )                                                                                       # one to many relationship. enables user.posts   Forward reference

    @property                                                                               # allows to get path in schemas.py (UserResponse) automatically (from_attributes = True)
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"
    

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),                                                             # this links to users
        nullable=False,
        index=True,                                                                         # makes queries faster, but slower writes (usually worth it)
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),                                                            # makes sure that timezone aware storage works (for Postgress later, sqlite uses text for time)
        default=lambda: datetime.now(UTC),
    )

    author: Mapped[User] = relationship(back_populates="posts")                             # many to one. allows post.author to get user. with this sqlalchemy auto handles joins