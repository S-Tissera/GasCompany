from sqlalchemy import Column, Integer, String
from app import db


class GasType(db.Model):
    __tablename__ = 'gastype'

    gasTypeID = Column(Integer, primary_key=True)
    typeName = Column(String(50), nullable=False)  # "Regular", "Industrial"
