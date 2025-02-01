from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    notificationID = Column(Integer, primary_key=True)
    userID = Column(Integer, ForeignKey('users.userID'), nullable=False)  # Corrected ForeignKey reference
    message = Column(String(500), nullable=False)
    sentAt = Column(DateTime, nullable=False)  # Corrected column name to match the schema

    # Relationships
    user = relationship("User", back_populates="notifications")

    @staticmethod
    def log_notification(user_id, message):
        notification = Notification(userID=user_id, message=message)
        db.session.add(notification)
        db.session.commit()
