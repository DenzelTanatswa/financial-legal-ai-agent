"""Development-only local authentication using salted Werkzeug password hashes."""
from werkzeug.security import check_password_hash, generate_password_hash
from core.database import SessionLocal, User, AuditLog, init_database


def register_user(email: str, password: str) -> User:
    init_database()
    email = email.strip().lower()
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    with SessionLocal() as db:
        if db.query(User).filter_by(email=email).first():
            raise ValueError("An account with this email already exists.")
        user = User(email=email, password_hash=generate_password_hash(password))
        db.add(user); db.flush()
        db.add(AuditLog(user_id=user.id, event="user_registered", metadata_json={}))
        db.commit(); db.refresh(user)
        return user


def authenticate_user(email: str, password: str) -> User | None:
    init_database()
    with SessionLocal() as db:
        user = db.query(User).filter_by(email=email.strip().lower()).first()
        if not user or not check_password_hash(user.password_hash, password):
            return None
        db.add(AuditLog(user_id=user.id, event="user_logged_in", metadata_json={}))
        db.commit(); db.expunge(user)
        return user
