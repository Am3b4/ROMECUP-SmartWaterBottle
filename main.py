from pydantic import BaseModel, Field, PastDate, AwareDatetime, field_validator
from auth import get_current_user, getUserExceptions
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from database import engine, SessionLocal
from datetime import date, datetime
from sqlalchemy.orm import Session

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

    @field_validator('dataNascita', mode='before')
    def parse_dd_mm_yyyy(cls, v):
        if bool(datetime.strptime(v, "%Y-%m-%d")):
            return v
        try:
            return datetime.strptime(v, '%d/%m/%Y').date()
        except Exception as e:
            raise ValueError("dataNascita must be in dd/mm/yyyy") from e

class UtenteLogin(BaseModel):

    username: str
    password: str


class FontanelleByRange(BaseModel):

    latitudine: float
    longitudine: float
    raggio: int = 500


@app.get("/user/private")
async def get_user(user: dict = Depends(get_current_user), db: Session = Depends(getDB)):
    if user is None:
        raise getUserExceptions()
    userModel = db.query(models.Utenti).filter(models.Utenti.id_utente == user["id"]).first()
    return userModel


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
        "dataRegistrazione": str(date.today()),
    }

    res = requests.post('http://127.0.0.1:9000/createUser', json=body)
    if res.status_code == 200:
        return res.json()
    return HTTPException(status_code=500, detail={})


@app.post("/login")
async def login(user: UtenteLogin):
    body = {
        "username": user.username,
        "password": user.password
    }
    token  = requests.post('http://127.0.0.1:9000/token', json=body)
    return token.json()


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')


@app.get("/fontanelle")
async def fontanelle(db: Session = Depends(getDB)):

    fontanelleDati = db.query(models.Fontanelle).all()
    print(type(fontanelleDati))
    return list(map(lambda x: {
        "id": x.id,
        "indirizzo": x.indirizzo,
        "latitudine": x.latitudine,
        "longitudine": x.longitudine,
        "tipo": x.tipo
    }, fontanelleDati
    ))

@app.post("/fontanelle/}")
async def fontanelle(info: FontanelleByRange, db: Session = Depends(getDB)):



def httpExceptionUserNotFound():
    raise HTTPException(status_code=404, detail="User not found")
