from app.email_reader import fetch_unread_emails
from app.task_detector import detect_task
from app.database import SessionLocal
from app.models import Ticket


def process_emails():
    emails = fetch_unread_emails()
    created = []

    for email in emails:
        result = detect_task(email["subject"], email["body"])

        if result["is_task"]:
            db = SessionLocal()
            try:
                ticket = Ticket(
                    title=result["title"],
                    description=result["description"],
                    assignee=result["assignee"],
                    priority=result["priority"] or "medium",
                )
                db.add(ticket)
                db.commit()
                db.refresh(ticket)
                created.append({"ticket_id": ticket.id, "title": ticket.title, "from": email["sender"]})
            finally:
                db.close()

    return {"emails_scanned": len(emails), "tickets_created": len(created), "tickets": created}
