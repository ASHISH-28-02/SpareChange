from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# --- User CRUD ---
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_balance(db: Session, user_id: int, main_balance_delta: float = 0, savings_balance_delta: float = 0):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.main_balance += main_balance_delta
        user.savings_balance += savings_balance_delta
        db.commit()
        db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# --- Transaction & Savings CRUD ---
def create_user_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.dict(), owner_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def create_savings_pot_entry(db: Session, amount: float, user_id: int, transaction_id: int):
    db_savings = models.SavingsPot(rounded_amount=amount, owner_id=user_id, transaction_id=transaction_id)
    db.add(db_savings)
    db.commit()
    db.refresh(db_savings)
    return db_savings

# --- Loan CRUD ---
def find_lender(db: Session, required_savings: float, borrower_id: int):
    """Finds a user with enough savings to be a lender, who is not the borrower."""
    return db.query(models.User).filter(
        models.User.id != borrower_id,
        models.User.savings_balance >= required_savings
    ).first()

def create_loan(db: Session, loan_request: schemas.LoanCreate, lender_id: int, borrower_id: int):
    # In a real app, this would be a more complex process with offers/acceptances.
    # Here, we create an active loan immediately.
    
    # Debit lender's savings, credit borrower's main balance
    update_user_balance(db, user_id=lender_id, savings_balance_delta=-loan_request.amount)
    update_user_balance(db, user_id=borrower_id, main_balance_delta=loan_request.amount)

    db_loan = models.Loan(
        amount=loan_request.amount,
        lender_id=lender_id,
        borrower_id=borrower_id,
        status="active" # Auto-approved for simplicity
    )
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def update_loan_status(db: Session, loan_id: int, status: str):
    loan = get_loan(db, loan_id)
    if loan:
        loan.status = status
        db.commit()
        db.refresh(loan)
    return loan
