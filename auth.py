from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import FastAPI, Depends, HTTPException, status
from datetime import date, datetime, timedelta
from database import SessionLocal, engine
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional

import sqlalchemy
import models

SECRET_KEY = ""
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.base.metadata.create_all(bind=engine)
oauth2Bearer = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

class Utente(BaseModel):

    username: str
    password: str
    nome: str
    cognome: str
    email: str
    sesso: str
    dataNascita: date
    dataRegistrazione: date

class UtenteLogin(BaseModel):
    username: str
    password: str


def getDB():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def getHashedPassword(password):
    return bcrypt_context.hash(password)

def verifyHashedPassword(hashedPassword, password):
    return bcrypt_context.verify(password, hashedPassword)

def authenticateUser(username: str, password: str, db: Session):
    user = db.query(models.Utenti).filter(models.Utenti.username == username).first()

    if not user:
        return False
    if not verifyHashedPassword(user.hashedPassword, password):
        return False
    return user


def createAccessToken(username: str, user_id: int, expiresDelta: Optional[timedelta] = None):
    encode = {'sub': username, 'id': user_id}
    if expiresDelta:
        expire = datetime.utcnow() + expiresDelta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2Bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if not username or not user_id:
            raise getUserExceptions()
        return {'username': username, 'id': user_id}
    except jwt.JWTError:
        raise getUserExceptions()

@app.post("/createUser")
async def createUser(utente: Utente, db: Session = Depends(getDB)):
    userModel = models.Utenti()

    hashedPassword = getHashedPassword(utente.password)

    userModel.username = utente.username
    userModel.hashedPassword = hashedPassword
    userModel.nome = utente.nome
    userModel.cognome = utente.cognome
    userModel.email = utente.email
    userModel.sesso = utente.sesso
    userModel.dataNascita = utente.dataNascita
    userModel.dataRegistrazione = utente.dataRegistrazione

    try:
        db.add(userModel)
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        return {
            'statusCode': '409',
            'message': 'User already exists'
        }

    return {
        'statusCode': 200,
        'description': 'success',
    }


@app.post("/token")
async def login_for_access_token(form_data: UtenteLogin, db: Session = Depends(getDB)):
    user = authenticateUser(form_data.username, form_data.password, db)
    if not user:
        raise tokenExceptions()

    token_expires = timedelta(minutes=25)
    token = createAccessToken(user.username, user.id_utente, token_expires)
    return {'access_token': token, 'token_type': 'bearer'}


# Exceptions

def getUserExceptions():
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return credentialsException

def tokenExceptions():
    tokenExceptionResponse = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )
    return tokenExceptionResponse

def httpExceptionUserNotFound():
    raise HTTPException(status_code=404, detail="User not found")
