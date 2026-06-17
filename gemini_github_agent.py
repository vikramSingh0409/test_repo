import os
import json
import asyncio

from dotenv import load_dotenv

from google import genai
from google.genai import types

from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
client = genai.Client(api_key=GEMINI_API_KEY)

EXCLUDED_TOOLS = {"issue_write"}


def clean_schema(obj):
    if isinstance(obj, dict):
        cleaned = {}

        for k, v in obj.items():
            if k in {
                "additionalProperties",
                "additional_properties",
                "$schema",
                "$defs",
                "examples",
                "default",
            }:
                continue

            cleaned[k] = clean_schema(v)

        return cleaned

    if isinstance(obj, list):
        return [clean_schema(x) for x in obj]

    return obj


async def main():

    mcp_client = MultiServerMCPClient(
        {
            "github": {
                "transport": "streamable_http",
                "url": os.environ["MCP_SERVER_URL"],
                "headers": {
                    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"
                },
            }
        }
    )

    tools = await mcp_client.get_tools()

    tool_map = {}
    gemini_tools = []

    for tool in tools:

        if tool.name in EXCLUDED_TOOLS:
            print(f"Skipping tool: {tool.name}")
            continue

        tool_map[tool.name] = tool

        schema = clean_schema(tool.args_schema)

        gemini_tools.append(
            types.FunctionDeclaration(
                name=tool.name,
                description=getattr(tool, "description", "") or "",
                parameters=schema,
            )
        )
    print(f"Registered tools: {len([tool.name for tool in tool_map.values()])}")
    user_prompt = input("\nAsk: ")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    function_declarations=gemini_tools
                )
            ]
        ),
    )

    candidate = response.candidates[0]
    part = candidate.content.parts[0]

    if not getattr(part, "function_call", None):
        print("\nAssistant:\n")
        print(response.text)
        return

    tool_name = part.function_call.name
    tool_args = dict(part.function_call.args)

    print("\nCalling MCP Tool:")
    print(tool_name)
    print(json.dumps(tool_args, indent=2))

    result = await tool_map[tool_name].ainvoke(tool_args)

    final_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            user_prompt,
            f"Tool result:\n{result}",
        ],
    )

    print("\nAssistant:\n")
    print(final_response.text)


if __name__ == "__main__":
    asyncio.run(main())