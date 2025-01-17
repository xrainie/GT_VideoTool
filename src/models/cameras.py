from sqlalchemy import Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base
from src.core.enums import CameraName


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(Enum(CameraName), index=True, nullable=True)
    rtps_url: Mapped[str] = mapped_column(String, nullable=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
