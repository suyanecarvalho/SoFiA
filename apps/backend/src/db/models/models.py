import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLAlchemyEnum,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.base import Base


class TransactionType(str, enum.Enum):
    EXPENSE = "expense"
    INCOME = "income"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile_pic = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    transactions = relationship("Transaction", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    transactions = relationship("Transaction", back_populates="category")
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    transaction_type = Column(SQLAlchemyEnum(TransactionType), nullable=False)
    is_superfluous = Column(Boolean, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=True)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    __table_args__ = (
        CheckConstraint(
            "(transaction_type = 'income' AND category_id IS NULL AND is_superfluous IS NULL) OR "
            "(transaction_type = 'expense' AND category_id IS NOT NULL)",
            name="ck_transaction_attributes",
        ),
    )
