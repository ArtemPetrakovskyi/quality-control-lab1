from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import database as db
from logger_config import privacy_logger

db.init_db()


def create_initial_data():
    session = db.SessionLocal()
    try:
        existing_user = session.query(db.User).filter_by(id=1).first()
        if not existing_user:
            test_user = db.User(
                id=1,
                name="Ivan Testov",
                email="ivan.test@example.com",
                phone="+380991112233",
                password_hash="secret_hashed_password_123"
            )
            session.add(test_user)
            session.commit()

            test_consent = db.Consent(
                user_id=1,
                purpose="MARKETING",
                is_granted=False,
                policy_version="v1.0"
            )
            session.add(test_consent)
            session.commit()
    finally:
        session.close()


create_initial_data()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_initial_data()
    yield


app = FastAPI(title="GDPR Privacy Engineering Demo", lifespan=lifespan)


def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/")
def read_root():
    return {"status": "System running"}


@app.get("/api/users/{user_id}/personal-data")
def export_personal_data(
        user_id: int,
        request_actor_id: int = 1,
        db_session: Session = Depends(get_db)
):
    if user_id != request_actor_id:
        privacy_logger.info(f"Unauthorized access attempt by actor={request_actor_id} for user={user_id}")
        raise HTTPException(status_code=403, detail="Access denied: Cannot access other user data")

    user = db_session.query(db.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    consents = db_session.query(db.Consent).filter_by(user_id=user_id).all()
    consents_data = [
        {
            "purpose": c.purpose,
            "is_granted": c.is_granted,
            "policy_version": c.policy_version,
            "updated_at": str(c.updated_at)
        }
        for c in consents
    ]

    privacy_logger.info(f"Data export executed for user_id={user_id}")

    return {
        "metadata": {"export_version": "1.0", "subject_id": user.id},
        "profile": {
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        },
        "consents": consents_data
    }


@app.post("/api/users/{user_id}/anonymize")
def anonymize_user(
        user_id: int,
        request_actor_id: int = 1,
        db_session: Session = Depends(get_db)
):
    if user_id != request_actor_id:
        raise HTTPException(status_code=403, detail="Access denied")

    user = db_session.query(db.User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = "Anonymous User"
    user.email = f"deleted_{user.id}@anon.local"
    user.phone = "+000000000000"
    user.password_hash = "[REDACTED]"

    db_session.commit()
    privacy_logger.info(f"User anonymized successfully for user_id={user_id}")

    return {"status": "Success", "message": "User PII has been irreversibly anonymized"}


@app.post("/api/consents/grant")
def grant_consent(user_id: int, purpose: str, db_session: Session = Depends(get_db)):
    consent = db_session.query(db.Consent).filter_by(user_id=user_id, purpose=purpose).first()
    if not consent:
        consent = db.Consent(user_id=user_id, purpose=purpose)
        db_session.add(consent)

    consent.is_granted = True
    consent.updated_at = datetime.utcnow()
    db_session.commit()
    return {"status": "Granted", "purpose": purpose}


@app.post("/api/consents/revoke")
def revoke_consent(user_id: int, purpose: str, db_session: Session = Depends(get_db)):
    consent = db_session.query(db.Consent).filter_by(user_id=user_id, purpose=purpose).first()
    if consent:
        consent.is_granted = False
        consent.updated_at = datetime.utcnow()
        db_session.commit()
    return {"status": "Revoked", "purpose": purpose}


def check_consent_policy(user_id: int, purpose: str, db_session: Session) -> bool:
    consent = db_session.query(db.Consent).filter_by(user_id=user_id, purpose=purpose).first()
    return consent.is_granted if consent else False


@app.post("/api/marketing/send")
def send_marketing_email(user_id: int, db_session: Session = Depends(get_db)):
    has_permission = check_consent_policy(user_id, "MARKETING", db_session)

    if not has_permission:
        privacy_logger.info(f"Action DENIED for user_id={user_id} due to missing consent")
        raise HTTPException(status_code=403, detail="Policy Gate: Consent for MARKETING is missing or revoked")

    privacy_logger.info(f"Marketing email sent to user_id={user_id}")
    return {"status": "Success", "message": "Marketing email sent!"}