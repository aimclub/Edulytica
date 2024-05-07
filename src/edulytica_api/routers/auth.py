from fastapi import Request

from fastapi import APIRouter


from src.edulytica_api.models import *
from src.edulytica_api.database import SessionLocal
import src.edulytica_api.schemas.auth as auth_schemas
import jwt
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from src.edulytica_api.routers.auth_bearer import JWTBearer


from src.edulytica_api.models.auth import User, Token
from src.edulytica_api.routers.utils import create_access_token, create_refresh_token, verify_password, get_hashed_password
from src.edulytica_api.settings import JWT_SECRET_KEY, ALGORITHM

auth_router = APIRouter()
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@auth_router.post('/login', response_model=auth_schemas.TokenSchema)
def login(request: auth_schemas.UserLogin, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == request.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    hashed_pass = user.password
    if not verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    token_db = Token(user_id=user.id, access_token=access, refresh_token=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token": access,
        "refresh_token": refresh,
    }

@auth_router.post("/register")
def register_user(user: auth_schemas.UserCreate, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    encrypted_password =get_hashed_password(user.password)

    new_user = User(username=user.username, email=user.email, password=encrypted_password)

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message":"user created successfully"}

@auth_router.post('/change-password')
def change_password(request: auth_schemas.changepassword, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == request.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")

    encrypted_password = get_hashed_password(request.new_password)
    user.password = encrypted_password
    db.commit()

    return {"message": "Password changed successfully"}


@auth_router.post('/logout')
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_record = db.query(Token).all()
    info = []
    for record in token_record:
        if (datetime.utcnow() - record.created_date).days > 1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(Token).where(Token.user_id.in_(info)).delete()
        db.commit()

    existing_token = db.query(Token).filter(Token.user_id == user_id,
                                                        Token.access_token == token).first()
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message": "Logout Successfully"}