# Productivity Assistant

A minimal personal productivity assistant that extracts calendar events from your emails and adds them to your calendar with human approval.

## Setup

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your actual API keys and MCP URLs
```

### 4. Required API Keys and Connections
- **Anthropic API Key**: Get from https://console.anthropic.com/
- **Gmail MCP**: Connect Gmail in your Claude.ai settings
- **Google Calendar MCP**: Connect Google Calendar in your Claude.ai settings

## Project Structure
```
productivity-assistant/
├── pyproject.toml       # Project dependencies
├── .env                 # Environment variables (not committed)
├── .env.example         # Example environment file
├── models.py            # Pydantic data models
├── mcp_client.py        # MCP server client wrapper (next step)
├── agent.py             # Agent logic (next step)
├── main.py              # FastAPI application (next step)
└── README.md            # This file
```

## Usage (after full implementation)
```bash
# Start the server
uv run uvicorn main:app --reload

# In another terminal, trigger email scan
curl -X POST http://localhost:8000/scan-emails

# Review and approve events
curl -X POST http://localhost:8000/approve/{session_id} \
  -H "Content-Type: application/json" \
  -d '{"approved_event_ids": ["event1", "event2"]}'
```

## Development Status
- [x] Project setup
- [x] Data models
- [ ] MCP client wrapper
- [ ] Agent logic
- [ ] FastAPI endpoints
- [ ] Testing

## Core Features
- Scans last 50 emails
- Extracts calendar events using Claude
- Human review before calendar updates
- Adds approved events to Google Calendar