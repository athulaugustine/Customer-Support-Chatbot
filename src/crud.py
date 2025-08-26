from src.models import Ticket
from src.db import SessionLocal
from langchain_core.tools import tool
from datetime import datetime
@tool
def create_ticket(user: str, subject: str, description: str) -> str:
    "Creates a new support ticket in the database with the given user, subject, and description."
    session = SessionLocal()
    ticket = Ticket(user=user, subject=subject, description=description)
    session.add(ticket)
    session.commit()
    return f"✅ Ticket #{ticket.id} created."
@tool
def update_ticket(ticket_id: int, status: str) -> str:
    "Updates the status of an existing ticket."
    session = SessionLocal()
    ticket = session.query(Ticket).filter_by(id=ticket_id).first()
    if not ticket:
        return "❌ Ticket not found."
    ticket.status = status
    session.commit()
    return f"✅ Ticket #{ticket_id} updated to '{status}'."
@tool
def delete_ticket(ticket_id: int) -> str:
    """Deletes a ticket from the system."""
    session = SessionLocal()
    ticket = session.query(Ticket).filter_by(id=ticket_id).first()
    if not ticket:
        return "❌ Ticket not found."
    session.delete(ticket)
    session.commit()
    return f"🗑️ Ticket #{ticket_id} deleted."
@tool
def check_ticket(ticket_id: int) -> str:
    """Retrieves basic information and status for a specific ticket."""
    session = SessionLocal()
    ticket = session.query(Ticket).filter_by(id=ticket_id).first()
    if not ticket:
        return "❌ Ticket not found."
    return f"📄 Ticket #{ticket.id} [{ticket.status}]: {ticket.subject}"
@tool
def list_tickets(user: str) -> str:
    """Lists all tickets submitted by a specific user."""
    session = SessionLocal()
    tickets = session.query(Ticket).filter_by(user=user).all()
    if not tickets:
        return f"No tickets found for user {user}."
    return "\n".join([f"#{t.id} - {t.subject} ({t.status})" for t in tickets])
@tool
def search_tickets(query: str) -> str:
    """Searches for tickets that contain the query string in the subject or description (case-insensitive)."""
    session = SessionLocal()
    results = session.query(Ticket).filter(
        Ticket.subject.ilike(f"%{query}%") |
        Ticket.description.ilike(f"%{query}%")
    ).all()
    if not results:
        return "No tickets matched your query."
    return "\n".join([f"#{t.id} - {t.subject} ({t.status})" for t in results])

@tool
def get_current_datetime() -> str:
    """Returns the current date and time in a human-readable format."""
    now = datetime.now()
    return now.strftime("🕒 %A, %d %B %Y, %I:%M %p")