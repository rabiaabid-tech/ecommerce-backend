from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import models, schemas, auth_utils
from database import get_db
import re
import os

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Admin emails from .env
ADMIN_EMAILS = os.getenv(
    "ADMIN_EMAILS", "admin@brand.com"
).split(",")

# ✅ Multiple domains allowed
ALLOWED_DOMAINS = [
    "@gmail.com", "@yahoo.com",
    "@outlook.com", "@hotmail.com"
]

def is_email_allowed(email: str) -> bool:
    return any(
        email.lower().endswith(d) for d in ALLOWED_DOMAINS
    )

def validate_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search("[a-zA-Z]", password):
        return False, "Must contain at least one letter."
    if not re.search("[0-9]", password):
        return False, "Must contain at least one number."
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Must contain at least one special character."
    return True, ""

# ── SIGNUP ──
@router.post(
    "/signup",
    response_model=schemas.UserResponse
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # ✅ Multiple domains check
    if not is_email_allowed(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please use Gmail, Yahoo, or Outlook email."
        )

    # Duplicate check
    existing = db.query(models.User).filter(
        models.User.email == user.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    # Password validation
    is_valid, error_msg = validate_password(user.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    hashed = auth_utils.get_password_hash(user.password)

    # ✅ Admin check case-insensitive
    user_is_admin = user.email.lower() in [
        e.lower().strip() for e in ADMIN_EMAILS
    ]

    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed,
        is_admin=user_is_admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ── LOGIN ──
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # ✅ Multiple domains check
    if not is_email_allowed(form_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Gmail, Yahoo, or Outlook accounts allowed."
        )

    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not user or not auth_utils.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires = timedelta(
        minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    token = auth_utils.create_access_token(
        data={
            "sub": user.email,
            "is_admin": user.is_admin,
            "full_name": user.full_name
        },
        expires_delta=expires
    )

    return {"access_token": token, "token_type": "bearer"}