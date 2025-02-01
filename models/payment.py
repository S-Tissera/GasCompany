from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app import db


class Payment(db.Model):
    __tablename__ = 'payments'

    paymentID = Column(Integer, primary_key=True)
    requestID = Column(Integer, ForeignKey('gas_request.requestID'), nullable=False)
    paymentDate = Column(DateTime, nullable=False)
    amountPaid = Column(Float, nullable=False)
    paymentMethod = Column(String(50), nullable=False)  # "Cash", "Credit Card", etc.
    status = Column(String(50), nullable=False)  # "Paid", "Pending", "Failed"

    # Relationships
    gas_request = relationship("GasRequest", back_populates="payments")
