from sqlite3 import DataError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import Contact, Address
from schemas import ContactCreate, ContactUpdate


def db_get_contacts(session: Session, offset: int = 0, limit: int = 100) -> list[Contact]:
    db_list_contacts = session.query(Contact).outerjoin(
        Contact.address).offset(offset).limit(limit).all()
    return db_list_contacts


def db_get_contacts_by_name(name: str, session: Session) -> list[Contact]:
    db_list_contacts = session.query(Contact).outerjoin(
        Contact.address).filter(Contact.name == name).all()
    return db_list_contacts


def db_get_contact_by_phone(phone: str, session: Session) -> Contact:
    db_contact = session.query(Contact).outerjoin(
        Contact.address).filter(Contact.phone == phone).first()
    return db_contact


def db_create_contact(contact: ContactCreate, session: Session) -> Contact:
    try:
        db_contact = Contact(
            name=contact.name,
            company=contact.company,
            phone=contact.phone,
            email=contact.email
        )
        session.add(db_contact)
        session.flush()

        if contact.address:
            db_address = Address(
                street=contact.address.street,
                zip_code=contact.address.zip_code,
                country=contact.address.country,
                contact_id=db_contact.id
            )
            session.add(db_address)

        session.commit()
        session.refresh(db_contact)
        return db_contact
    except SQLAlchemyError:
        session.rollback()
        raise


def db_delete_contact(phone: str, session: Session) -> Contact:
    db_contact = session.query(Contact).outerjoin(
        Contact.address).filter(Contact.phone == phone).first()

    if not db_contact:
        return None

    session.delete(db_contact)
    session.commit()
    return db_contact


def db_update_contact(phone: str, contact: ContactUpdate, session: Session) -> Contact:
    try:

        db_contact = session.query(Contact).outerjoin(
            Contact.address).filter(Contact.phone == phone).first()

        if not db_contact:
            return None

        updated_data = contact.model_dump(exclude_unset=True)

        if "address" in updated_data:
            updated_address = updated_data.pop("address")
            if db_contact.address:
                for key, value in updated_address.items():
                    setattr(db_contact.address, key, value)
            else:
                new_address = Address(
                    **updated_address, contact_id=db_contact.id)
                session.add(new_address)

        for key, value in updated_data.items():
            setattr(db_contact, key, value)

        session.commit()
        session.refresh(db_contact)
        return db_contact
    except SQLAlchemyError:
        session.rollback()
        raise
