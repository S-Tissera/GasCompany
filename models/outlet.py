from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app import db

# Import GasStock to ensure it's defined before the relationship is created
from models.gas_stock import GasStock

class Outlet(db.Model):
    __tablename__ = 'outlets'

    outletID = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    managerID = Column(Integer, ForeignKey('users.userID'), nullable=False)  # ForeignKey to User
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime, nullable=False)

    # Relationships
    gas_requests = relationship("GasRequest", back_populates="outlet")
    delivery_schedules = relationship("DeliverySchedule", back_populates="outlet")
    gas_stocks = relationship("GasStock", back_populates="outlet")  # This relationship should work now
