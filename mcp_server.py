from mcp.server.fastmcp import FastMCP
from app.database import SessionLocal
from app.models import Ticket

mcp = FastMCP("ticket-agent")


@mcp.tool()
def create_ticket(title: str, description: str = "", assignee: str = "", priority: str = "medium") -> dict:
    """Create a new ticket."""
    db = SessionLocal()
    try:
        ticket = Ticket(
            title=title,
            description=description or None,
            assignee=assignee or None,
            priority=priority,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return {"id": ticket.id, "title": ticket.title, "status": ticket.status, "priority": ticket.priority}
    finally:
        db.close()


@mcp.tool()
def list_tickets(status: str = "") -> list:
    """List all tickets. Optionally filter by status (open, closed, in_progress)."""
    db = SessionLocal()
    try:
        query = db.query(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        tickets = query.all()
        return [
            {"id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "assignee": t.assignee}
            for t in tickets
        ]
    finally:
        db.close()


@mcp.tool()
def get_ticket(ticket_id: int) -> dict:
    """Get full details of a ticket by ID."""
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        return {
            "id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "assignee": ticket.assignee,
            "priority": ticket.priority,
            "status": ticket.status,
            "created_at": str(ticket.created_at),
        }
    finally:
        db.close()


@mcp.tool()
def update_ticket(ticket_id: int, status: str = "", assignee: str = "", priority: str = "") -> dict:
    """Update a ticket's status, assignee, or priority."""
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        if status:
            ticket.status = status
        if assignee:
            ticket.assignee = assignee
        if priority:
            ticket.priority = priority
        db.commit()
        db.refresh(ticket)
        return {"id": ticket.id, "title": ticket.title, "status": ticket.status, "priority": ticket.priority}
    finally:
        db.close()


@mcp.tool()
def resolve_ticket(ticket_id: int) -> dict:
    """Mark a ticket as resolved."""
    db = SessionLocal()
    try:
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}
        ticket.status = "resolved"
        db.commit()
        return {"id": ticket.id, "title": ticket.title, "status": ticket.status}
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()
