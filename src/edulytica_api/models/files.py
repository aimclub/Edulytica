from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.edulytica_api.database import Base

class FileStatus(Base):
    __tablename__ = "filestatuses"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    files: Mapped[List["Files"]] = relationship(back_populates="status")
class Files(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file = Column(String)
    data_create = Column(String)
    status_id: Mapped[int] = mapped_column(ForeignKey("filestatuses.id"))
    status: Mapped["FileStatus"] = relationship(back_populates="files")