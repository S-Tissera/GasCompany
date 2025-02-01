from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app import db


class DeliverySchedule(db.Model):
    __tablename__ = 'deliveryschedule'

    scheduleID = Column(Integer, primary_key=True)
    outletID = Column(Integer, ForeignKey('outlets.outletID'), nullable=False)  # ForeignKey to 'outlets.outletID'
    dispatchDate = Column(DateTime, nullable=False)
    deliveryDate = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)  # "Scheduled", "Completed", etc.

    # Relationships
    outlet = relationship("Outlet", back_populates="delivery_schedules")  # This should work correctly now
