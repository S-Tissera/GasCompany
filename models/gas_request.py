from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app import db
import uuid

class GasRequest(db.Model):
    __tablename__ = 'gas_requests'

    requestID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('users.userID'), nullable=False)
    outletID = Column(Integer, ForeignKey('outlets.outletID'), nullable=False)
    requestedDate = Column(DateTime, nullable=False)
    pickupPeriodStart = Column(DateTime, nullable=True)
    pickupPeriodEnd = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)
    totalAmount = Column(Integer, nullable=True)
    reallocated = Column(Integer, nullable=True)
    token = Column(String(255), unique=True, nullable=True)  # New Token Column

    # Relationships
    user = relationship("User", back_populates="gas_requests")
    outlet = relationship("Outlet", back_populates="gas_requests")

    @staticmethod
    def generate_token():
        """Generate a unique token for gas requests."""
        return str(uuid.uuid4())  # Generates a random unique token
