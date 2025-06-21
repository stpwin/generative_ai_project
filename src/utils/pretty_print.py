"""
Pretty printing utilities for LLM responses and other data structures.
"""

import json
import pprint
from typing import Any, Dict, List, Optional


def pretty_print_response(response: Any, title: str = "LLM Response") -> None:
    """
    Pretty print an LLM response object with multiple formatting options.

    Args:
        response: The LLM response object to print
        title: Title to display above the formatted output
    """
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

    # Method 1: Using pprint for clean formatting
    # print("\n--- Method 1: Using pprint ---")
    # pprint.pprint(response, width=80, depth=None)

    # # Method 2: Convert to dict and pretty print JSON
    # print("\n--- Method 2: JSON formatting ---")
    # try:
    #     response_dict = response.model_dump() if hasattr(response, 'model_dump') else dict(response)
    #     print(json.dumps(response_dict, indent=2, ensure_ascii=False))
    # except Exception as e:
    #     print(f"Could not convert to JSON: {e}")

    # Method 3: Custom formatted output for key fields
    # print("\n--- Method 3: Custom formatted key fields ---")
    try:
        # print(f"Model: {response.model}")
        # print(f"ID: {response.id}")
        # print(f"Created: {response.created}")
        # print(f"Usage: {response.usage}")

        for i, choice in enumerate(response.choices):
            print(f"\nChoice {i}:")
            print(f"  Finish Reason: {choice.finish_reason}")
            print(f"  Message Role: {choice.message.role}")
            print(f"  Message Content: {choice.message.content}")
            if choice.message.tool_calls:
                print(f"  Tool Calls: {len(choice.message.tool_calls)}")
                for j, tool_call in enumerate(choice.message.tool_calls):
                    print(f"    Tool Call {j}:")
                    print(f"      ID: {tool_call.id}")
                    print(f"      Function: {tool_call.function.name}")
                    print(f"      Arguments: {tool_call.function.arguments}")
    except Exception as e:
        print(f"Could not format custom fields: {e}")


def pretty_print_json(data: Any, title: str = "JSON Data", indent: int = 2) -> None:
    """
    Pretty print JSON data with proper formatting.

    Args:
        data: The data to print as JSON
        title: Title to display above the JSON
        indent: Number of spaces for indentation
    """
    print(f"\n{'='*40}")
    print(f"{title}")
    print(f"{'='*40}")

    try:
        if isinstance(data, str):
            # Try to parse if it's a JSON string
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass

        print(json.dumps(data, indent=indent, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Could not format as JSON: {e}")
        print(f"Raw data: {data}")


def pretty_print_dict(data: Dict[str, Any], title: str = "Dictionary", max_width: int = 80) -> None:
    """
    Pretty print a dictionary with clean formatting.

    Args:
        data: Dictionary to print
        title: Title to display above the dictionary
        max_width: Maximum width for formatting
    """
    print(f"\n{'='*40}")
    print(f"{title}")
    print(f"{'='*40}")

    pprint.pprint(data, width=max_width, depth=None)


def pretty_print_list(data: List[Any], title: str = "List", max_items: Optional[int] = None) -> None:
    """
    Pretty print a list with clean formatting.

    Args:
        data: List to print
        title: Title to display above the list
        max_items: Maximum number of items to display (None for all)
    """
    print(f"\n{'='*40}")
    print(f"{title}")
    print(f"{'='*40}")

    items_to_show = data[:max_items] if max_items else data

    for i, item in enumerate(items_to_show):
        print(f"[{i}] {item}")

    if max_items and len(data) > max_items:
        print(f"... and {len(data) - max_items} more items")


def pretty_print_messages(messages: List[Dict[str, Any]], title: str = "Messages") -> None:
    """
    Pretty print a list of chat messages.

    Args:
        messages: List of message dictionaries
        title: Title to display above the messages
    """
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")

    for i, message in enumerate(messages):
        role = message.get('role', 'unknown')
        content = message.get('content', '')

        print(f"\n--- Message {i+1} ({role.upper()}) ---")
        print(content)

        # Handle tool calls if present
        if 'tool_calls' in message and message['tool_calls']:
            print(f"\nTool Calls ({len(message['tool_calls'])}):")
            for j, tool_call in enumerate(message['tool_calls']):
                print(f"  {j+1}. {tool_call.get('function', {}).get('name', 'unknown')}")
                print(f"     Args: {tool_call.get('function', {}).get('arguments', '')}")

        # Handle tool responses
        if message.get('role') == 'tool':
            print(f"Tool: {message.get('name', 'unknown')}")
            print(f"Response: {content}")


def pretty_print_tokens_usage(usage: Any, title: str = "Token Usage") -> None:
    """
    Pretty print token usage information.

    Args:
        usage: Usage object or dictionary
        title: Title to display above the usage info
    """
    print(f"\n{'='*30}")
    print(f"{title}")
    print(f"{'='*30}")

    try:
        if hasattr(usage, 'model_dump'):
            usage_dict = usage.model_dump()
        elif hasattr(usage, '__dict__'):
            usage_dict = usage.__dict__
        else:
            usage_dict = dict(usage)

        for key, value in usage_dict.items():
            print(f"{key.replace('_', ' ').title()}: {value:,}")

    except Exception as e:
        print(f"Could not format usage: {e}")
        print(f"Raw usage: {usage}")


# Convenience function for quick debugging
def pp(data: Any, title: str = "Debug Output") -> None:
    """
    Quick pretty print function for debugging.

    Args:
        data: Any data to print
        title: Title for the output
    """
    print(f"\n🔍 {title}")
    print("-" * (len(title) + 4))
    pprint.pprint(data, width=100, depth=None)
