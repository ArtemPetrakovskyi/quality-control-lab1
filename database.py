from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    password_hash = Column(String)

    consents = relationship("Consent", back_populates="owner")

class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    purpose = Column(String)
    is_granted = Column(Boolean, default=False)
    policy_version = Column(String, default="v1.0")
    updated_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="consents")

def init_db():
    Base.metadata.create_all(bind=engine)