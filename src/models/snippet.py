from sqlalchemy import ForeignKey, String, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class CodeSnippet(Base, TimestampMixin, SoftDeleteMixin):
    """Code snippet model."""
    __tablename__ = "code_snippets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))

    category: Mapped["Category"] = relationship()

    def __init__(self, **kwargs):
        if "name" in kwargs and "title" not in kwargs:
            kwargs["title"] = kwargs.pop("name")
        if "content" in kwargs and "code" not in kwargs:
            kwargs["code"] = kwargs.pop("content")
        if "language" not in kwargs:
            kwargs["language"] = "plaintext"
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return self.title

    @name.setter
    def name(self, val: str):
        self.title = val

    @property
    def content(self) -> str:
        return self.code

    @content.setter
    def content(self, val: str):
        self.code = val


Snippet = CodeSnippet
