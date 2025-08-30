from pydantic import BaseModel
from typing import List, Optional
import datetime

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    amount: float
    description: str

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    owner_id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


# --- Savings Schemas ---
class SavingsPot(BaseModel):
    id: int
    rounded_amount: float
    timestamp: datetime.datetime
    owner_id: int

    class Config:
        from_attributes = True


# --- Loan Schemas ---
class LoanBase(BaseModel):
    amount: float
    borrower_id: int

class LoanCreate(LoanBase):
    pass

class LoanOffer(BaseModel):
    loan_id: int

class Loan(LoanBase):
    id: int
    lender_id: int
    interest_rate: float
    status: str
    creation_date: datetime.datetime
    due_date: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    main_balance: float
    savings_balance: float
    transactions: List[Transaction] = []
    savings: List[SavingsPot] = []
    loans_lent: List[Loan] = []
    loans_borrowed: List[Loan] = []

    class Config:
        from_attributes = True


# --- Token Schemas for Authentication ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
