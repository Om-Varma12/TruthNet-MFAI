import json
import os

from groq import Groq

from services.search_service import tavily_search


def build_support_with_llm(title, domain, ml_result):
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        fallback_query = f"{title} fact check {domain}"
        return {
            "generated_query": fallback_query,
            "search_results": tavily_search(fallback_query, num=5),
            "reason": "GROQ_API_KEY missing. Returned model-only reasoning.",
        }

    client = Groq(api_key=groq_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "tavily_search",
                "description": "Search public web for fact-checking evidence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "num": {"type": "integer"},
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    first_messages = [
        {
            "role": "system",
            "content": "You are a fact-check assistant. Create a focused query and call tavily_search.",
        },
        {
            "role": "user",
            "content": (
                "Generate a strong fact-check query and call the tool.\n"
                f"Title: {title}\n"
                f"Domain: {domain}\n"
                f"Model verdict: {ml_result['label']}\n"
                f"Model signals: {json.dumps(ml_result['model_signals'])}"
            ),
        },
    ]

    first = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=first_messages,
        tools=tools,
        tool_choice="auto",
    )

    message = first.choices[0].message
    generated_query = f"{title} fact check"
    search_results = []

    if message.tool_calls:
        call = message.tool_calls[0]
        args = json.loads(call.function.arguments)
        generated_query = args.get("query", generated_query)
        num = int(args.get("num", 5))
        search_results = tavily_search(generated_query, num=num)

        second_messages = first_messages + [
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": "tavily_search",
                            "arguments": call.function.arguments,
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": "tavily_search",
                "content": json.dumps(search_results),
            },
            {
                "role": "user",
                "content": (
                    "Based on model signals + search results, write concise reasoning: "
                    "why this is likely real or fake."
                ),
            },
        ]

        second = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=second_messages,
        )
        reason = second.choices[0].message.content or "No explanation generated."
    else:
        generated_query = f"{title} fact check {domain}"
        search_results = tavily_search(generated_query, num=5)
        reason = "No tool call generated. Used fallback query."

    return {
        "generated_query": generated_query,
        "search_results": search_results,
        "reason": reason,
    }
