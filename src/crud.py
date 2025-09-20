from typing import Optional, List
from contextlib import contextmanager
from datetime import datetime

from langchain_core.tools import tool
from sqlalchemy import or_

from src.models import Ticket, TicketStatus, PriorityLevel
from src.db import SessionLocal  # keep your existing SessionLocal

# ---- Helpers ----
@contextmanager
def get_session():
    """Context manager for sessions with commit/rollback behavior."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _parse_enum_member(enum_class, value: str):
    """
    Parse user-provided enum value to enum member.
    Accepts:
      - enum member name ("open", "in_progress")
      - enum value ("Open", "In Progress")
      - case-insensitive
    Raises ValueError if not found.
    """
    if value is None:
        raise ValueError("Enum value is required")
    value_str = str(value).strip()
    # exact name (case-insensitive)
    for member in enum_class:
        if value_str.lower() == member.name.lower() or value_str.lower() == str(member.value).lower():
            return member
    raise ValueError(f"Unknown {enum_class.__name__} value: {value!r}")


def _format_ticket_list(tickets: List[Ticket]) -> str:
    lines = []
    for t in tickets:
        lines.append(f"#{t.id} — {t.subject} [{t.status.value}] (priority: {t.priority.value})")
    return "\n".join(lines)


# ---- Tools (LangChain tool-wrapped functions) ----
@tool
def create_ticket(user: str, subject: str, description: str, priority: Optional[str] = "medium", category: Optional[str] = None) -> str:
    """Create a new support ticket. Returns a friendly confirmation string."""
    if not (user and subject and description):
        return "❌ Missing required fields: 'user', 'subject', and 'description' are required."

    try:
        priority_member = _parse_enum_member(PriorityLevel, priority)
    except ValueError:
        priority_member = PriorityLevel.medium

    with get_session() as session:
        ticket = Ticket(
            user=user.strip(),
            subject=subject.strip(),
            description=description.strip(),
            priority=priority_member,
            category=category.strip() if category else None,
        )
        session.add(ticket)
        # commit happens in context manager
        session.flush()  # ensure id is populated
        return f"✅ Ticket created: #{ticket.id} — {ticket.subject}"


@tool
def update_ticket(ticket_id: str, status: Optional[str] = None, assigned_to: Optional[str] = None, priority: Optional[str] = None) -> str:
    """Update ticket fields. ticket_id must be the ticket UUID string."""
    with get_session() as session:
        ticket = session.query(Ticket).filter_by(id=str(ticket_id)).first()
        if not ticket:
            return "❌ Ticket not found."

        changed = []
        if status is not None:
            try:
                ticket.status = _parse_enum_member(TicketStatus, status)
                changed.append("status")
                # set closed_at automatically if closed
                if ticket.status == TicketStatus.closed and ticket.closed_at is None:
                    ticket.closed_at = datetime.utcnow()
                elif ticket.status != TicketStatus.closed:
                    ticket.closed_at = None
            except ValueError as e:
                return f"❌ {e}"

        if priority is not None:
            try:
                ticket.priority = _parse_enum_member(PriorityLevel, priority)
                changed.append("priority")
            except ValueError as e:
                return f"❌ {e}"

        if assigned_to is not None:
            ticket.assigned_to = assigned_to.strip() if assigned_to else None
            changed.append("assigned_to")

        if not changed:
            return "⚠️ Nothing to update. Provide at least one updatable field (status, assigned_to, priority)."

        session.add(ticket)
        return f"✅ Ticket #{ticket.id} updated ({', '.join(changed)})."


@tool
def delete_ticket(ticket_id: str) -> str:
    """Delete a ticket by id."""
    with get_session() as session:
        ticket = session.query(Ticket).filter_by(id=str(ticket_id)).first()
        if not ticket:
            return "❌ Ticket not found."
        session.delete(ticket)
        return f"🗑️ Ticket #{ticket_id} deleted."


@tool
def check_ticket(ticket_id: str) -> str:
    """Return a short summary of a ticket."""
    with get_session() as session:
        ticket = session.query(Ticket).filter_by(id=str(ticket_id)).first()
        if not ticket:
            return "❌ Ticket not found."
        t = ticket
        return (
            f"📄 Ticket #{t.id}\n"
            f"Subject: {t.subject}\n"
            f"Status: {t.status.value}\n"
            f"Priority: {t.priority.value}\n"
            f"Assigned to: {t.assigned_to or '—'}\n"
            f"Created: {t.created_at.isoformat() if t.created_at else '—'}"
        )


@tool
def list_tickets(user: str, limit: int = 50) -> str:
    """List tickets for a user (most recent first)."""
    with get_session() as session:
        tickets = session.query(Ticket).filter_by(user=user).order_by(Ticket.created_at.desc()).limit(int(limit)).all()
        if not tickets:
            return f"No tickets found for user {user}."
        return _format_ticket_list(tickets)


@tool
def search_tickets(query: str, limit: int = 50) -> str:
    """Search subject and description (case-insensitive)."""
    q = str(query).strip()
    if not q:
        return "❌ Please provide a search query."

    with get_session() as session:
        results = (
            session.query(Ticket)
            .filter(or_(Ticket.subject.ilike(f"%{q}%"), Ticket.description.ilike(f"%{q}%")))
            .order_by(Ticket.created_at.desc())
            .limit(int(limit))
            .all()
        )
        if not results:
            return "No tickets matched your query."
        return _format_ticket_list(results)


@tool
def get_current_datetime() -> str:
    """Returns the current server date/time in a human-friendly format."""
    now = datetime.now()
    # e.g. 🕒 Sunday, 21 September 2025, 03:15 PM
    return now.strftime("🕒 %A, %d %B %Y, %I:%M %p")
