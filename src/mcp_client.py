import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def run_mlops_query(question: str) -> dict:
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.mcp_server"],
        cwd=str(ROOT_DIR),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema,
                    }
                }
                for t in tools_result.tools
            ]

            print(f"GPT discovered {len(tools)} MLOps tools")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an MLOps engineer. Use the available tools to answer "
                        "questions about model health, drift, and alerts. "
                        "Always check the fleet status first, then drill into specific models."
                    )
                },
                {"role": "user", "content": question}
            ]

            while True:
                response = _client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )

                msg = response.choices[0].message

                if msg.tool_calls:
                    messages.append({"role": "assistant", "content": msg.content, "tool_calls": [
                        {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls
                    ]})

                    for tc in msg.tool_calls:
                        print(f"GPT calling tool: {tc.function.name}")
                        args = json.loads(tc.function.arguments)
                        result = await session.call_tool(tc.function.name, arguments=args)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result.content[0].text,
                        })
                else:
                    return {
                        "question": question,
                        "answer": msg.content,
                    }


def ask_mlops(question: str) -> dict:
    return asyncio.run(run_mlops_query(question))


if __name__ == "__main__":
    questions = [
        "Which models in the fleet need immediate attention?",
        "What is the drift status of credit_scorer_v1?",
        "Give me a summary of all active alerts.",
    ]

    for q in questions:
        print(f"\n{'='*60}")
        print(f"QUESTION: {q}")
        result = ask_mlops(q)
        print(f"\nANSWER:\n{result['answer']}")