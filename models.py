from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from database import base


class Utenti(base):
    __tablename__ = 'Utenti'

    id_utente = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False)
    hashedPassword = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    cognome = Column(String, nullable=False)
    sesso = Column(String, nullable=False)
    dataNascita = Column(DateTime, nullable=False)
    dataRegistrazione = Column(DateTime, nullable=False)


class Fontanelle(base):
    __tablename__ = 'Fontanelle'

    id_fontanelle = Column(Integer, primary_key=True)
    indirizzo = Column(String, nullable=False)
    latitudine = Column(Float(precision=64), nullable=False)
    longitudine = Column(Float(precision=64), nullable=False)

