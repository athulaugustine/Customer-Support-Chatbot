import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PriorityLevel(enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    urgent = "Urgent"


class TicketStatus(enum.Enum):
    open = "Open"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user = Column(String(100), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    priority = Column(Enum(PriorityLevel), default=PriorityLevel.medium, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.open, nullable=False)

    assigned_to = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Ticket(id={self.id}, subject='{self.subject}', status='{self.status.name}')>"