from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field, PastDate, AwareDatetime
from auth import get_current_user, getUserExceptions
from fastapi import FastAPI, Depends, HTTPException
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from datetime import date

import requests
import models


app = FastAPI()
models.base.metadata.create_all(bind=engine)


def getDB():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Utente(BaseModel):

    username: str
    password: str
    nome: str
    cognome: str
    email: str
    sesso: str
    dataNascita: date
    dataRegistrazione: date


@app.get("/")
async def readAll(db: Session = Depends(getDB)):
    return db.query(models.Utenti).all()

@app.get("/user/private")
async def get_user(user: dict = Depends(get_current_user), db: Session = Depends(getDB)):
    if user is None:
        raise getUserExceptions()
    userModel = db.query(models.Utenti).filter(models.Utenti.id_utente == user["id"]).first()
    return userModel

@app.get("/users/{user_id}")
async def readUser(user_id: int, db: Session = Depends(getDB)):
    user_model = db.query(models.Utenti).filter(models.Utenti.id_utente == user_id).first()
    if not user_model:
        httpExceptionUserNotFound()
    return user_model


@app.post("/register")
async def register(user: Utente):
    body = {
        "username": user.username,
        "password": user.password,
        "nome": user.nome,
        "cognome": user.cognome,
        "email": user.email,
        "sesso": user.sesso,
        "dataNascita": str(user.dataNascita),
        "dataRegistrazione": str(user.dataRegistrazione),
    }

    res = requests.post('http://127.0.0.1:9000/createUser', json=body)
    if res.status_code == 200:
        return res.json()
    return HTTPException(status_code=500, detail={})


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    body = {
        "username": form_data.username,
        "password": form_data.password,
    }
    res = requests.post('http://127.0.0.1:9000/token', json=body)
    print(res.json())
    return res.json()

def httpExceptionUserNotFound():
    raise HTTPException(status_code=404, detail="User not found")
