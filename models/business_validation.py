from sqlalchemy import Column, Integer, String, ForeignKey
from app import db


class BusinessValidation(db.Model):
    __tablename__ = 'business_requests'

    validationID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('user.userID'), nullable=False)
    businessName = Column(String(100), nullable=False)
    certificationDocument = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # "Pending", "Validated", "Rejected"
