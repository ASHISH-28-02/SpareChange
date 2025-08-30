from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    """
    User model representing a user in the database.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    main_balance = Column(Float, default=10000.0) # Starting with a mock balance
    savings_balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

    transactions = relationship("Transaction", back_populates="owner")
    savings = relationship("SavingsPot", back_populates="owner")
    loans_lent = relationship("Loan", foreign_keys="[Loan.lender_id]", back_populates="lender")
    loans_borrowed = relationship("Loan", foreign_keys="[Loan.borrower_id]", back_populates="borrower")

class Transaction(Base):
    """
    Transaction model for recording user spending.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="transactions")
    savings_entry = relationship("SavingsPot", back_populates="transaction", uselist=False)

class SavingsPot(Base):
    """
    SavingsPot model for recording the rounded-up savings.
    """
    __tablename__ = "savings_pots"

    id = Column(Integer, primary_key=True, index=True)
    rounded_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    transaction_id = Column(Integer, ForeignKey("transactions.id"))

    owner = relationship("User", back_populates="savings")
    transaction = relationship("Transaction", back_populates="savings_entry")

class Loan(Base):
    """
    Loan model for peer-to-peer lending.
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False, default=0.05) # 5% interest rate
    status = Column(String, default="pending") # pending, active, paid, defaulted
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    due_date = Column(DateTime, nullable=True)

    lender_id = Column(Integer, ForeignKey("users.id"))
    borrower_id = Column(Integer, ForeignKey("users.id"))

    lender = relationship("User", foreign_keys=[lender_id], back_populates="loans_lent")
    borrower = relationship("User", foreign_keys=[borrower_id], back_populates="loans_borrowed")
