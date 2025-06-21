from dotenv import load_dotenv
from openai import OpenAI
import json
import sys
import os
import uuid
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("LITELLM_PROXY_API_KEY"),
    base_url=os.environ.get("LITELLM_PROXY_API_BASE"),
)

# Add the src directory to the path so we can import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from utils.pretty_print import (
    pretty_print_response,
    pretty_print_messages,
)

SYSTEM_PROMPT = (
    "You are a snarky assistant.\n<current_datetime>"
    + datetime.now().isoformat()
    + "</current_datetime>"
)
MODEL = "scb10x/llama3.1-typhoon2-8b-instruct"

session_id = str(uuid.uuid4())

print("Session ID:", session_id)


def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": "celsius"})
    elif "san francisco" in location.lower():
        return json.dumps(
            {"location": "San Francisco", "temperature": "72", "unit": "fahrenheit"}
        )
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": "celsius"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def think(thought):
    """Think something"""
    # return json.dumps({"thought": thought})
    return thought


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "think",
            "description": "Use the tool to think about something. It will not obtain new information or change the database, but just append the thought to the log. Use it when complex reasoning or some cache memory is needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "A thought to think about.",
                    }
                },
                "required": ["thought"],
            },
        },
    },
]

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    },
    {
        "role": "user",
        "content": "What time is it?",
    },
]

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tool_choice="auto",
    tools=tools,
    extra_body={"litellm_session_id": session_id},
)

pretty_print_response(response, "First LLM Response")
pretty_print_messages(messages, "Conversation Messages")
# pretty_print_tokens_usage(response.usage, "Token Usage")

response_message = response.choices[0].message
tool_calls = response_message.tool_calls

print("\tTool calls", tool_calls)

# Print all tool call names clearly separated from other output
# if tool_calls:
#     print("\n" + "="*50)
#     print("TOOL CALLS MADE BY AI:")
#     print("="*50)
#     for i, tool_call in enumerate(tool_calls, 1):
#         print(f"{i}. Tool Name: {tool_call.function.name}")
#     print("="*50 + "\n")

if tool_calls:
    available_functions = {
        "get_current_weather": get_current_weather,
        "think": think,
    }
    messages.append(response_message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        print("function_args", function_args)
        function_response = function_to_call(**function_args)

        # Add context to tool response to prevent AI confusion
        contextual_response = (
            f"Tool '{function_name}' executed successfully. Result: {function_response}"
        )

        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": contextual_response,
            }
        )
    second_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        extra_body={"litellm_session_id": session_id},
    )
    pretty_print_response(second_response, "Second LLM Response")


print(response_message.content)
