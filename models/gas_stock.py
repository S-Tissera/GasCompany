from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app import db

class GasStock(db.Model):
    __tablename__ = 'stock'

    stockID = Column(Integer, primary_key=True)
    outletID = Column(Integer, ForeignKey('outlets.outletID'), nullable=False)
    gasTypeID = Column(Integer, ForeignKey('gas_type.gasTypeID'), nullable=False)
    quantity = Column(Integer, nullable=False)
    lastUpdated = Column(DateTime, nullable=False)

    # Relationships
    outlet = relationship("Outlet", back_populates="gas_stocks")
