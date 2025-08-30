import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define the database file path
# In a real application, this would be a more robust database like PostgreSQL
SQLALCHEMY_DATABASE_URL = "sqlite:///./microsavings.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class which will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our models to inherit from
Base = declarative_base()

def init_db():
    """
    Initializes the database and creates tables if they don't exist.
    """
    # Import all models here so that they are registered on the metadata
    from . import models
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Dependency to get a database session for each request.
    Yields a session and ensures it's closed afterward.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
