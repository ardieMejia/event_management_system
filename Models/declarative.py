# ========== this file mostly for the bulk upload of Excel, not sure if its better to remove this completely, might confuse other programmers
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Date, Float, Integer, String


class EventListing(Base):
    __tablename__ = 'event'
    
    id = Column(Integer, primary_key=True)
    tournamentName = Column(String(128))
    
    startDate = Column(String(64))
    endDate = Column(String(64))
    
    discipline = Column(String(64))
