from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    rtps_url: Mapped[str] = mapped_column(String)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
