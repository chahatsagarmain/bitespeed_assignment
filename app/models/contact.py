from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base

class LinkPrecedenceEnum(str, Enum):
    primary = "primary"
    secondary = "secondary"

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    linkPrecedence = Column(String, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)

    # define relationship to self for linked contacts
    secondaries = relationship("Contact", remote_side=[id])
