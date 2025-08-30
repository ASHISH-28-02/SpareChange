from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import math
import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext
from transformers import pipeline
import json

# Import local modules
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db

# --- Configuration ---
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
# This is no longer used for loan decisions, but kept for other potential features
IBM_GRANITE_API_URL = "https://your-ibm-granite-api-endpoint.com/v1/generate" 
IBM_API_KEY = "your-ibm-api-key" 

# --- Initialization ---
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# --- Load Hugging Face Model on Startup ---
credit_risk_analyzer = None
try:
    print("INFO:     Loading Hugging Face model for credit risk analysis...")
    # Using a reliable sentiment analysis model for finance
    credit_risk_analyzer = pipeline("sentiment-analysis", model="ProsusAI/finbert")
    print("INFO:     Hugging Face model loaded successfully.")
except Exception as e:
    print(f"ERROR:    Could not load Hugging Face model. Credit risk analysis will be disabled. Error: {e}")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Utility Functions ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# --- API Endpoints ---

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.post("/users/me/transactions/", response_model=schemas.Transaction)
def create_transaction_for_user(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    original_amount = transaction.amount
    rounded_up_amount = math.ceil(original_amount / 10) * 10
    savings_amount = rounded_up_amount - original_amount
    if current_user.main_balance < rounded_up_amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    crud.update_user_balance(db, user_id=current_user.id, main_balance_delta=-rounded_up_amount, savings_balance_delta=savings_amount)
    db_transaction = crud.create_user_transaction(db=db, transaction=transaction, user_id=current_user.id)
    crud.create_savings_pot_entry(db=db, amount=savings_amount, user_id=current_user.id, transaction_id=db_transaction.id)
    payout_threshold = 1000
    user = crud.get_user(db, user_id=current_user.id)
    if user.savings_balance >= payout_threshold:
        print(f"INFO: Payout of {payout_threshold} triggered for user {user.username}")
        crud.update_user_balance(db, user_id=user.id, main_balance_delta=payout_threshold, savings_balance_delta=-payout_threshold)
    return db_transaction

@app.post("/loans/request") # Note: response_model removed for flexible response
def request_loan(
    loan_request: schemas.LoanCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    if not credit_risk_analyzer:
        raise HTTPException(status_code=503, detail="Credit risk analysis service is currently unavailable.")

    # 1. Gather user's financial data
    transaction_count = len(current_user.transactions)
    savings_balance = current_user.savings_balance
    repaid_loans = sum(1 for loan in current_user.loans_borrowed if loan.status == 'paid')
    active_loans = sum(1 for loan in current_user.loans_borrowed if loan.status == 'active')

    # 2. Create a financial summary for the AI to analyze
    financial_summary = (
        f"User has made {transaction_count} transactions, has a savings balance of {savings_balance:.2f} rupees, "
        f"has successfully repaid {repaid_loans} loans, and currently has {active_loans} active loans."
    )
    
    # 3. Get the AI's sentiment analysis
    try:
        result = credit_risk_analyzer(financial_summary)
        sentiment = result[0]['label'].lower()
        print(f"INFO:     AI Credit Risk Analysis for {current_user.username}:")
        print(f"INFO:     Summary: {financial_summary}")
        print(f"INFO:     Predicted Sentiment: {sentiment}")
    except Exception as e:
        print(f"ERROR:    Hugging Face model failed to analyze text: {e}")
        raise HTTPException(status_code=500, detail="Credit risk analysis failed due to an internal error.")

    # 4. Make a decision and generate a reason
    if sentiment == 'negative':
        reason = "Loan denied. Our AI analysis suggests a high credit risk based on your current financial profile."
        raise HTTPException(status_code=400, detail=reason)
    else: # 'positive' or 'neutral'
        reason = "Loan approved! Our AI analysis of your financial profile shows a positive outlook."

    # 5. If approved, find a lender and create the loan
    lender = crud.find_lender(db, required_savings=loan_request.amount, borrower_id=current_user.id)
    if not lender:
        raise HTTPException(status_code=404, detail="Loan approved, but no available lenders with sufficient funds.")

    created_loan = crud.create_loan(db=db, loan_request=loan_request, lender_id=lender.id, borrower_id=current_user.id)
    
    loan_details = schemas.Loan.from_orm(created_loan).model_dump()
    return {"loan_details": loan_details, "explanation": reason}


@app.post("/loans/repay/{loan_id}")
def repay_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    loan = crud.get_loan(db, loan_id=loan_id)
    if not loan or loan.borrower_id != current_user.id:
        raise HTTPException(status_code=404, detail="Loan not found or you are not the borrower.")
    if loan.status != 'active':
        raise HTTPException(status_code=400, detail=f"Loan is not active. Current status: {loan.status}")

    interest_amount = loan.amount * loan.interest_rate
    repayment_amount = loan.amount + interest_amount 

    if current_user.main_balance < repayment_amount:
        raise HTTPException(status_code=400, detail="Insufficient funds to repay the loan.")

    crud.update_user_balance(db, user_id=current_user.id, main_balance_delta=-repayment_amount)
    crud.update_user_balance(db, user_id=loan.lender_id, savings_balance_delta=repayment_amount)
    crud.update_loan_status(db, loan_id=loan_id, status="paid")
    
    return {"message": f"Loan repaid successfully. Total amount paid (including interest): {repayment_amount:.2f}"}

@app.get("/insights")
async def get_financial_insights(current_user: schemas.User = Depends(get_current_user)):
    transaction_descriptions = [t.description for t in current_user.transactions[-10:]]
    prompt = f"Based on these recent spending categories, provide some brief, actionable financial advice for a user in India: {', '.join(transaction_descriptions)}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IBM_GRANITE_API_URL,
                headers={"Authorization": f"Bearer {IBM_API_KEY}", "Content-Type": "application/json"},
                json={"prompt": prompt, "max_tokens": 100},
                timeout=20.0
            )
            response.raise_for_status()
            insights = response.json().get("generations")[0].get("text")
            return {"insights": insights}
    except httpx.RequestError as e:
        print(f"Error calling IBM Granite API: {e}")
        return {"insights": "Could not fetch AI insights at the moment. General advice: Track your spending and build a budget to help you save more effectively!"}

