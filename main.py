from typing import Annotated
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Depends, HTTPException

from database import engine, get_session
from helpers import db_create_contact, db_delete_contact, db_get_contact_by_phone, db_get_contacts, db_get_contacts_by_name, db_update_contact
from models import Base
from schemas import Contact, ContactCreate, ContactUpdate


def create_db_and_tables():
    Base.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

SessionDep = Annotated[Session, Depends(get_session)]
app = FastAPI(lifespan=lifespan)


@app.get("/contacts")
def read_contacts(session: SessionDep, offset: int = 0, limit: int = 100) -> list[Contact]:
    list_contacts = db_get_contacts(session, offset, limit)
    return list_contacts


@app.get("/contacts/{name}")
def read_contacts_by_name(name: str, session: SessionDep) -> list[Contact]:
    list_contacts = db_get_contacts_by_name(name, session)
    return list_contacts


@app.get("/contact/{phone}")
def read_contact_by_phone(phone: str, session: SessionDep) -> Contact:
    contact = db_get_contact_by_phone(phone, session)
    return contact


@app.post("/contacts")
def create_contact(contact: ContactCreate, session: SessionDep) -> Contact:
    try:
        new_contact = db_create_contact(contact, session)
        return new_contact
    except IntegrityError:
        raise HTTPException(
            status_code=409, detail="Contact with this phone number already exists in the database.")


@app.delete("/contact/{phone}")
def delete_contact(phone: str, session: SessionDep) -> Contact:
    deleted_contact = db_delete_contact(phone, session)

    if not deleted_contact:
        raise HTTPException(
            status_code=404, detail="Contact with this phone number does not exists in the database.")

    return deleted_contact


@app.patch("/contact/{phone}")
def update_contact(phone: str, contact: ContactUpdate, session: SessionDep) -> Contact:
    try:
        updated_contact = db_update_contact(phone, contact, session)

        if not updated_contact:
            raise HTTPException(
                status_code=404, detail="Contact with this phone number does not exists in the database.")

        return updated_contact
    except IndexError:
        raise HTTPException(
            status_code=409, detail="Contact with this phone number already exists in the database.")
