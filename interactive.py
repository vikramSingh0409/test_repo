"""
Interactive CLI – chat with the GitHub MCP agent in a loop.
Type  'exit'  or  'quit'  to stop.
"""

import asyncio
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    google_api_key=os.environ["GEMINI_API_KEY"],
)

GITHUB_PAT = os.environ["GITHUB_PAT"]
GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


async def chat_loop() -> None:
    print("🔌 Connecting to GitHub remote MCP server…")
    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": GITHUB_MCP_URL,
                "headers": {"Authorization": f"Bearer {GITHUB_PAT}"},
            }
        }
    )
    tools = await client.get_tools()
    print(f"✅ Connected – {len(tools)} tools available.\n")

    agent = create_react_agent(llm, tools)

    history: list = []
    print("💬 GitHub MCP Agent – type 'exit' to quit\n" + "─" * 50)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Bye!")
            break

        history.append(HumanMessage(content=user_input))
        result = await agent.ainvoke({"messages": history})

        # Append all new messages to history so context is preserved
        new_messages = result["messages"][len(history):]
        history.extend(new_messages)

        # Find the last AI text reply
        reply = "(no response)"
        for msg in reversed(new_messages):
            if isinstance(msg, AIMessage) and msg.content:
                reply = msg.content
                break

        print(f"\nAgent: {reply}\n")


if __name__ == "__main__":
    asyncio.run(chat_loop())