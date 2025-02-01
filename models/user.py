from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app import db

class User(db.Model):
    __tablename__ = 'users'

    userID = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    nic = Column(String(12), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    role = Column(String(50), nullable=False)  # "Consumer", "Outlet Manager", etc.
    password = Column(String(255), nullable=False)

    # Relationships
    gas_requests = relationship("GasRequest", back_populates="user")
    notifications = relationship("Notification", back_populates="user")  # Ensure this matches the Notification model
