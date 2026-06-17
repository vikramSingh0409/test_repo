# LangGraph Agent with GitHub Remote MCP Server

A minimal but complete ReAct agent that connects to **GitHub's official managed MCP endpoint** (`https://api.githubcopilot.com/mcp/`) via [`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters).

```
You ──► agent.py / interactive.py
              │
         LangGraph ReAct Agent
              │
    MultiServerMCPClient (streamable_http)
              │
    https://api.githubcopilot.com/mcp/   ← GitHub remote MCP server
              │
         GitHub APIs (repos, issues, PRs, code search, …)
```

## Files

| File | Purpose |
|------|---------|
| `agent.py` | Single-shot query – run once and exit |
| `interactive.py` | Multi-turn CLI chat with memory |
| `.env.example` | Copy to `.env` and add your keys |
| `requirements.txt` | Python dependencies |

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set credentials
cp .env.example .env
#   Fill in ANTHROPIC_API_KEY and GITHUB_PAT

# 3a. Single query
python agent.py

# 3b. Interactive chat
python interactive.py
```

## Getting a GitHub PAT

1. Go to <https://github.com/settings/tokens>
2. Generate a **classic token** (or fine-grained) with at least:
   - `repo` – read/write access to repositories
   - `read:user`, `read:org` – profile/org metadata
3. Paste the token as `GITHUB_PAT` in your `.env`.

## Switching to OpenAI

Replace the `llm` in `agent.py`:

```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o", api_key=os.environ["OPENAI_API_KEY"])
```

## Read-only mode

Pass an extra header to prevent the agent from writing anything:

```python
"headers": {
    "Authorization": f"Bearer {GITHUB_PAT}",
    "X-MCP-Readonly": "true",   # ← read-only toolset
},
```

## Available GitHub MCP toolsets

| Toolset | URL suffix |
|---------|------------|
| All tools (default) | `/mcp/` |
| Actions / CI-CD | `/mcp/x/actions` |
| Issues | `/mcp/x/issues` |
| Pull Requests | `/mcp/x/pull_requests` |
| Code Security | `/mcp/x/code_security` |
| Discussions | `/mcp/x/discussions` |