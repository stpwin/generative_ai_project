from litellm import completion, supports_function_calling
import litellm
import json
import sys
import os
import uuid
from litellm.caching.caching import Cache

litellm.cache = Cache()

# Add the src directory to the path so we can import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from utils.pretty_print import (
    pretty_print_response,
    pretty_print_messages,
    pretty_print_tokens_usage,
    pp,
)

model = "litellm_proxy/scb10x/llama3.1-typhoon2-8b-instruct"
session_id = str(uuid.uuid4())

print("Session ID:", session_id)

assert supports_function_calling(model=model) == False


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
    return json.dumps({"thought": thought})


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
            "input_schema": {
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
        "content": "You are a snarky assistant.\nYou can call tool any time you want",
    },
    {
        "role": "user",
        "content": "What you think about you?",
    },
]

response = completion(
    model=model,
    messages=messages,
    tool_choice="auto",
    tools=tools,
    metadata={
        "litellm_session_id": session_id,
    },
    caching=True,
)

# Pretty print the first response using our utility
pretty_print_response(response, "First LLM Response")

# Also demonstrate other pretty print functions
pretty_print_messages(messages, "Conversation Messages")
pretty_print_tokens_usage(response.usage, "Token Usage")

response_message = response.choices[0].message
tool_calls = response_message.tool_calls

print("\nLength of tool calls", tool_calls, len(tool_calls))

if tool_calls:
    available_functions = {"get_current_weather": get_current_weather, "think": think}
    messages.append(response_message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        print("function_args", function_args)
        function_response = function_to_call(**function_args)
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
    second_response = completion(
        model=model,
        messages=messages,
        metadata={"litellm_session_id": session_id},
        caching=True,
    )  # get a new response from the model where it can see the function response
    pretty_print_response(second_response, "Second LLM Response")


print(response_message.content)
