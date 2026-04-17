import json
import os

from groq import Groq

from services.search_service import tavily_search

SYSTEM_PROMPT = '''
    You are an AI system that determines whether a news headline is FAKE or REAL based strictly on a provided news article.

    Task:
    Given a headline and its corresponding article, classify the headline.

    Definitions:
    - REAL: The headline is accurate and supported by the article.
    - FAKE: The headline is misleading, exaggerated, or not supported by the article.

    Rules:
    1. Use ONLY the information in the article.
    2. If the headline adds claims not clearly supported, classify as FAKE.
    3. Be strict about factual alignment.

    Output format:
    Return ONLY a valid JSON object:
    {
    "label": "REAL" or "FAKE",
    "confidence": float (0 to 1)
    }

    Do not include any additional text.

    ---

    Few-shot examples:

    Example 1:
    Headline: "Government bans all private vehicles nationwide"
    Article: "The government announced restrictions on private vehicles in select urban areas during peak hours to reduce pollution."
    Output:
    {
    "label": "FAKE",
    "confidence": 0.96
    }

    Example 2:
    Headline: "Study finds daily exercise improves mental health"
    Article: "Researchers found that individuals who exercised daily reported lower stress levels and improved mental well-being."
    Output:
    {
    "label": "REAL",
    "confidence": 0.97
    }

    Example 3:
    Headline: "New tax policy eliminates income tax for all citizens"
    Article: "The new policy reduces income tax rates for middle-income groups but does not eliminate taxes entirely."
    Output:
    {
    "label": "FAKE",
    "confidence": 0.95
    }

    Example 4:
    Headline: "Heavy rains cause flooding in Mumbai suburbs"
    Article: "Continuous heavy rainfall over two days led to waterlogging and flooding in several Mumbai suburban areas."
    Output:
    {
    "label": "REAL",
    "confidence": 0.98
    }
'''

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
            model="openai/gpt-oss-120b",
            messages=second_messages,
        )
        reason = second.choices[0].message.content or "No explanation generated."
    else:
        generated_query = f"{title} fact check {domain}"
        search_results = tavily_search(generated_query, num=5)
        reason = "No tool call generated. Used fallback query."



    final_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": json.dumps({
                "title": title,
                "search_results": search_results
            }),
        },
    ]

    final = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=final_messages,
    )

    final_verdict_raw = final.choices[0].message.content or "{}"

    try:
        final_verdict = json.loads(final_verdict_raw)
    except:
        final_verdict = {
            "label": "UNKNOWN",
            "confidence": 0.0
    }

    return {
        "generated_query": generated_query,
        "search_results": search_results,
        "reason": reason,
        "final_verdict": final_verdict
    }