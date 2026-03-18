# Ticket Agent

An AI-powered ticket management system built for developer teams. Ticket Agent connects your inbox to your issue tracker — using Claude to read incoming emails, detect actionable tasks, and automatically create tickets. It also exposes an MCP server so AI coding agents can create, update, and resolve tickets through natural language during their workflow.

---

## What It Does

**Autonomous email-to-ticket pipeline**
Ticket Agent polls your Gmail inbox on a schedule. For each new email, it asks Claude: *"is there a task in here?"* If yes, it extracts the title, description, priority, and assignee, and creates a ticket automatically — no human input required.

**MCP server for AI coding agents**
AI coding agents like Claude Code can create and manage tickets directly through conversation. Say *"create a high priority ticket for the login bug"* and the agent handles it using the exposed MCP tools.

**Web dashboard**
A clean, real-time dashboard lets you view all tickets, filter by status, and manually trigger an email scan.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Ticket Agent                        │
│                                                         │
│   ┌─────────────┐     ┌──────────────┐                 │
│   │  Gmail API  │────▶│ Task Detector│                 │
│   │ (email_     │     │ (Claude      │                 │
│   │  reader.py) │     │  Haiku)      │                 │
│   └─────────────┘     └──────┬───────┘                 │
│                              │ detected task            │
│                              ▼                          │
│                    ┌──────────────────┐                 │
│                    │  SQLite Database │                 │
│                    │  (tickets.db)    │                 │
│                    └──────┬───────────┘                 │
│                           │                             │
│            ┌──────────────┼──────────────┐             │
│            ▼              ▼              ▼             │
│      ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│      │ REST API │  │   MCP    │  │   Web    │        │
│      │(FastAPI) │  │  Server  │  │Dashboard │        │
│      └──────────┘  └──────────┘  └──────────┘        │
│            ▲              ▲                            │
│            │              │                            │
│      HTTP clients    AI agents                         │
│                    (Claude Code)                        │
└─────────────────────────────────────────────────────────┘
```

**Request flows:**

- **Email pipeline:** APScheduler triggers every 5 minutes → Gmail API fetches unread emails → Claude Haiku classifies each email → ticket created in SQLite if task detected
- **MCP flow:** AI agent calls MCP tool → `mcp_server.py` reads/writes SQLite directly
- **REST flow:** HTTP client calls FastAPI → routes read/write SQLite via SQLAlchemy

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Web framework | FastAPI | Async-first, automatic API docs, dependency injection |
| Database | SQLite + SQLAlchemy | Zero-config, file-based, ORM for clean models |
| AI (task detection) | Claude Haiku (Anthropic API) | Fast, cheap, accurate for classification tasks |
| Agent protocol | MCP (Model Context Protocol) | Standard interface for AI agent tool use |
| Email | Gmail API (OAuth2) | Secure, no password storage |
| Scheduler | APScheduler | Background jobs without a separate process |
| Validation | Pydantic | Request/response schema validation |

---

## Project Structure

```
ticket-agent/
├── main.py                  # FastAPI app, scheduler startup, dashboard route
├── mcp_server.py            # MCP server exposing ticket tools to AI agents
├── requirements.txt
├── .env.example
│
├── app/
│   ├── database.py          # SQLAlchemy engine and session management
│   ├── models.py            # Ticket database model
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── routes.py            # CRUD REST endpoints
│   ├── email_reader.py      # Gmail OAuth2 connection and email fetching
│   ├── task_detector.py     # Claude integration for task classification
│   └── email_processor.py  # Orchestrates email → ticket pipeline
│
└── templates/
    └── dashboard.html       # Web dashboard (vanilla JS, no build step)
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- An [Anthropic API key](https://console.anthropic.com)
- A Google Cloud project with the Gmail API enabled and OAuth credentials

### 1. Clone and install

```bash
git clone https://github.com/codingWizard-Nikhil/ticket-agent.git
cd ticket-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Set up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a project
2. Enable the Gmail API
3. Create an OAuth 2.0 client ID (Desktop app type)
4. Download the credentials JSON and save it as `credentials.json` in the project root
5. Add your Gmail address as a test user under **APIs & Services → OAuth consent screen**

On first run, a browser window will open asking you to authorize access. After that, a `token.json` is saved and reused automatically.

### 4. Run

```bash
source .venv/bin/activate
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) for the dashboard.

The email processor runs automatically every 5 minutes. To trigger it manually, hit the "Check Emails" button in the dashboard or:

```bash
curl -X POST http://localhost:8000/process-emails
```

---

## REST API

Full interactive docs available at [http://localhost:8000/docs](http://localhost:8000/docs) when the server is running.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web dashboard |
| `GET` | `/tickets/` | List all tickets |
| `POST` | `/tickets/` | Create a ticket |
| `GET` | `/tickets/{id}` | Get a ticket |
| `PATCH` | `/tickets/{id}` | Update a ticket |
| `DELETE` | `/tickets/{id}` | Delete a ticket |
| `POST` | `/process-emails` | Manually trigger email scan |
| `GET` | `/health` | Health check |

**Create a ticket:**
```bash
curl -X POST http://localhost:8000/tickets/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Fix login bug", "priority": "high", "assignee": "sarah"}'
```

---

## MCP Server

Ticket Agent exposes an MCP server so AI coding agents can interact with tickets through natural language.

### Available tools

| Tool | Description |
|---|---|
| `create_ticket` | Create a new ticket with title, description, priority, and assignee |
| `list_tickets` | List all tickets, optionally filtered by status |
| `get_ticket` | Get full details of a ticket by ID |
| `update_ticket` | Update a ticket's status, assignee, or priority |
| `resolve_ticket` | Mark a ticket as resolved |

### Connect to Claude Code

```bash
claude mcp add ticket-agent .venv/bin/python -- mcp_server.py
```

Once connected, you can manage tickets directly from a Claude Code session:

> *"Create a high priority ticket for the broken checkout flow and assign it to the backend team"*

> *"List all open tickets"*

> *"Resolve ticket 12"*

---

## Ticket Model

| Field | Type | Description |
|---|---|---|
| `id` | integer | Auto-generated unique identifier |
| `title` | string | Short description of the task |
| `description` | text | Full details |
| `assignee` | string | Person responsible |
| `deadline` | datetime | Optional due date |
| `priority` | string | `low`, `medium`, or `high` |
| `status` | string | `open`, `in_progress`, `resolved`, or `closed` |
| `created_at` | datetime | Timestamp set by the database |

---

## How the Email Pipeline Works

1. **Fetch** — Gmail API retrieves unread emails from your inbox
2. **Classify** — Each email's subject and body are sent to Claude Haiku with a structured prompt asking it to determine if the email contains an actionable task
3. **Extract** — If a task is detected, Claude returns a structured JSON object with the title, description, priority, and assignee parsed from the email content
4. **Create** — A ticket is automatically created in the database with the extracted fields

This runs on a 5-minute polling interval via APScheduler, running in a background thread alongside the FastAPI server.

**Example:** An email with the subject *"Bug: checkout broken on mobile"* and body *"Users on iOS can't complete purchases. Needs urgent fix. Assign to the payments team."* would automatically produce:

```json
{
  "title": "Fix broken checkout on mobile (iOS)",
  "description": "Users on iOS cannot complete purchases.",
  "priority": "high",
  "assignee": "payments team"
}
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key for Claude access |

---

## License

MIT
