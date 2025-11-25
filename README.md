# Productivity Assistant Agent

A personal productivity assistant designed to interact with your Gmail and Google Calendar via a natural language chat interface. This agent leverages Anthropic's Claude to orchestrate tool use with local Message Context Processor (MCP) servers for Gmail and Google Calendar.

## Architecture Overview

This project implements an AI agent where:
- The `main.py` script runs an interactive terminal chat interface.
- User commands in natural language are sent to Anthropic's Claude.
- Claude, acting as the orchestrator, decides which local MCP tools (Gmail or Google Calendar) to use based on the user's request.
- The `MCPClient` manages the lifecycle of the local MCP servers (Gmail and Calendar) via standard I/O (stdio) communication using the `mcp` SDK.
- The local MCP servers (implemented using `FastMCP`) then interact with the respective Google APIs (Gmail and Google Calendar) to perform actions like listing emails, getting email content, creating, listing, searching, or deleting calendar events.

## Project Structure

```
productivity-assistant/
├── pyproject.toml       # Project dependencies
├── .env                 # Environment variables (MUST BE CONFIGURED)
├── .env.example         # Example environment file
├── README.md            # This file
├── productivity_assistant/
│   ├── __init__.py
│   ├── agent.py             # Agent logic (minimal, orchestrates via MCPClient)
│   ├── main.py              # Main interactive chat loop entry point
│   ├── mcp_client.py        # Handles communication with Claude and local MCP servers
│   ├── models.py            # Pydantic data models for structured data
│   ├── servers/             # Contains local MCP server implementations
│   │   ├── calendar_server.py   # FastMCP server for Google Calendar
│   │   └── gmail_server.py      # FastMCP server for Gmail
│   ├── tests.py             # Unit tests
│   └── tools/               # Contains shared tools used by MCP servers
│       ├── calendar_tool.py     # Calendar API interaction logic
│       ├── gmail_tool.py        # Gmail API interaction logic
│       └── google_api_service.py # Shared Google API service builder
```

## Setup Instructions

### 1. Prerequisites

*   **Python 3.8+** (recommended via `pyenv` or `conda`)
*   `uv` for dependency management (install via `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`)
*   **Google Cloud Project:**
    *   Enable **Google Calendar API** and **Gmail API** for your project.
    *   Create an **OAuth 2.0 Client ID** of type **"Desktop app"**.
    *   Download the `client_secret.json` file. Place it in your project's root directory (e.g., as `./client_secret.json`).

### 2. Configure Environment Variables

1.  **Create `.env` file:** Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
2.  **Edit `.env`:** Open the newly created `.env` file and fill in the following:
    ```
    # Your Anthropic API Key (e.g., sk-ant-api03-...)
    ANTHROPIC_API_KEY=your_anthropic_api_key_here

    # MCP Server URLs from your Claude.ai "Connected Accounts" settings
    # These are used by 'mcp install' to register with Claude Desktop
    GMAIL_MCP_URL=https://mcp.gmail.com/sse
    CALENDAR_MCP_URL=https://mcp.calendar.google.com/sse

    # Path to your Google API client_secret.json file (downloaded from Google Cloud Console)
    # This single file is used for both Calendar and Gmail APIs.
    GOOGLE_API_CLIENT_SECRET_FILE=./client_secret.json
    ```

### 3. Install Dependencies

1.  **Activate your virtual environment.** If you don't have one, `uv` will create it.
    ```bash
    source .venv/bin/activate
    ```
2.  **Install project dependencies:**
    ```bash
    uv pip install -e .
    ```

### 4. Install MCPs in Claude Desktop

This step registers your local MCP servers with the Claude Desktop application.

1.  Open a terminal window and navigate to your project's root directory.
2.  Ensure your virtual environment is active.
3.  **Install the Calendar MCP:**
    ```bash
    mcp install productivity_assistant/servers/calendar_server.py
    ```
    *   You should see a "Successfully installed Google Calendar in Claude app" message.
4.  **Install the Gmail MCP:**
    ```bash
    mcp install productivity_assistant/servers/gmail_server.py
    ```
    *   You should see a "Successfully installed Google Gmail in Claude app" message.
5.  **Crucially: Close and re-open your Claude Desktop application** after both installs to ensure it registers the new MCPs correctly.

## Running the Agent

You only need **one terminal window** for this! Your `main.py` script will handle starting and managing the MCP servers.

1.  Open your terminal and navigate to your project's root directory.
2.  **Activate your virtual environment:**
    ```bash
    source .venv/bin/activate
    ```
3.  **Run the chat agent script:**
    ```bash
    python productivity_assistant/main.py
    ```
4.  **Google Authentication:**
    *   The first time your agent initializes the Calendar and Gmail MCPs, a browser window will open for *each* service asking you to authenticate with Google.
    *   Follow the prompts to grant access. This will create `token_files` (e.g., `token_gmail_v1.json`, `token_calendar_v3.json`) in your `productivity_assistant/tools` directory.

### Interacting with the Agent

Once `productivity_assistant/main.py` is running, you can chat with your agent directly in the terminal. Claude will interpret your natural language requests and orchestrate the necessary tool calls.

**Example Commands:**

*   `List my 5 most recent emails.`
*   `Create a meeting called 'Project Sync' for tomorrow at 10 AM for 1 hour.`
*   `Create an event for dinner with friends on December 25th at 7 PM.`
*   `Search my calendar for events about 'Gemini CLI'.`
*   `Get the body of email with ID: <email_id_from_list_emails>.`
*   `Delete the event with ID: <event_id_from_calendar_listing>.`
*   `quit` (to exit the chat)
