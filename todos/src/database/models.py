
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    CheckConstraint, 
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    created_at = Column(Date, default=date.today)
    password = Column(String(512), nullable=False)

    __table_args__ = (
        CheckConstraint("length(password) >=8", name="password_len_constraint"),
    )


class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False, index=True)
    description = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(User)
