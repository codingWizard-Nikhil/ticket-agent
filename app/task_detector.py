import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def detect_task(email_subject: str, email_body: str) -> dict:
    """
    Send email content to Claude and ask if it contains a task.
    Returns a dict with: is_task, title, description, priority, assignee
    """
    prompt = f"""You are analyzing an email to determine if it contains an actionable task or bug report that should become a ticket.

Email subject: {email_subject}
Email body: {email_body}

Respond with a JSON object in this exact format:
{{
    "is_task": true or false,
    "title": "short title if is_task, else null",
    "description": "full description if is_task, else null",
    "priority": "low, medium, or high if is_task, else null",
    "assignee": "person's name if mentioned, else null"
}}

Only respond with the JSON object, nothing else."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    result = json.loads(text)
    return result
