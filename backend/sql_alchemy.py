import enum
from typing import List, Optional
from sqlalchemy import (
    create_engine, Column, ForeignKey, Table, Text, Boolean, String, Date, 
    Time, DateTime, Float, Integer, Enum
)
from sqlalchemy.orm import (
    column_property, DeclarativeBase, Mapped, mapped_column, relationship
)
from datetime import datetime as dt_datetime, time as dt_time, date as dt_date

class Base(DeclarativeBase):
    pass



# Tables definition for many-to-many relationships

# Tables definition
class Record(Base):
    __tablename__ = "record"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt_date] = mapped_column(Date)
    numberOfPushups: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))


#--- Relationships of the record table
Record.user: Mapped["User"] = relationship("User", back_populates="hasRecords", foreign_keys=[Record.user_id])

#--- Relationships of the user table
User.hasRecords: Mapped[List["Record"]] = relationship("Record", back_populates="user", foreign_keys=[Record.user_id])

# Database connection
DATABASE_URL = "sqlite:///Class_Diagram.db"  # SQLite connection
engine = create_engine(DATABASE_URL, echo=True)

# Create tables in the database
Base.metadata.create_all(engine, checkfirst=True)