from typing import Optional

from pydantic import BaseModel, Field

# Address


class AddressBase(BaseModel):
    street: str = Field(min_length=3, max_length=100)
    zip_code: Optional[str] = Field(None, min_length=6, max_length=10)
    country: Optional[str] = Field(None, min_length=2, max_length=50)


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AddressBase):
    street: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None


class Address(AddressBase):
    id: int

    class Config:
        from_attributes = True

# Contact


class ContactBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    company: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: str = Field(min_length=9, max_length=30,
                       pattern=r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$")
    email: Optional[str] = Field(None, min_length=5,
                                 max_length=50, pattern=r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+")


class ContactCreate(ContactBase):
    address: Optional[AddressCreate] = None


class ContactUpdate(ContactBase):
    name: Optional[str] = None
    company: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    address: Optional[AddressUpdate] = None


class Contact(ContactBase):
    id: int
    address: Optional[Address] = None

    class Config:
        from_attributes = True
