"""
Demonstration of various pretty printing utilities for LLM responses and data structures.
"""

import json
import sys
import os
from datetime import datetime

# Add the src directory to the path so we can import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from utils.pretty_print import (
    pretty_print_json,
    pretty_print_dict,
    pretty_print_list,
    pretty_print_messages,
    pp
)

def demo_pretty_printing():
    """Demonstrate various pretty printing functions"""

    print("🎨 Pretty Printing Demonstration")
    print("=" * 50)

    # Demo 1: Pretty print JSON data
    sample_json = {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "response": {
            "content": "Hello, world!",
            "role": "assistant",
            "timestamp": datetime.now().isoformat()
        },
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 25,
            "total_tokens": 75
        }
    }

    pretty_print_json(sample_json, "Sample LLM Configuration")

    # Demo 2: Pretty print dictionary
    config_dict = {
        "api_endpoint": "https://api.openai.com/v1",
        "model_settings": {
            "temperature": 0.8,
            "top_p": 0.9,
            "frequency_penalty": 0.1
        },
        "features": ["chat", "completion", "embeddings"],
        "enabled": True
    }

    pretty_print_dict(config_dict, "Configuration Dictionary")

    # Demo 3: Pretty print list
    model_list = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-opus",
        "llama-2-70b",
        "mistral-7b"
    ]

    pretty_print_list(model_list, "Available Models", max_items=3)

    # Demo 4: Pretty print messages
    conversation = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant specialized in explaining complex topics."
        },
        {
            "role": "user",
            "content": "Can you explain how neural networks work?"
        },
        {
            "role": "assistant",
            "content": "Neural networks are computational models inspired by biological neural networks...",
            "tool_calls": [
                {
                    "function": {
                        "name": "search_knowledge_base",
                        "arguments": '{"query": "neural networks basics"}'
                    }
                }
            ]
        },
        {
            "role": "tool",
            "name": "search_knowledge_base",
            "content": "Found 15 relevant articles about neural networks..."
        }
    ]

    pretty_print_messages(conversation, "AI Conversation")

    # Demo 5: Quick debug printing with pp()
    debug_data = {
        "request_id": "req_123456",
        "processing_time": 1.25,
        "tokens_processed": 150,
        "model_response": {
            "confidence": 0.95,
            "categories": ["technical", "educational"],
            "metadata": {
                "source": "knowledge_base",
                "last_updated": "2024-01-15"
            }
        }
    }

    pp(debug_data, "Debug Information")

    # Demo 6: Pretty print complex nested structure
    complex_structure = {
        "llm_responses": [
            {
                "id": "resp_001",
                "model": "gpt-4",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "This is a sample response"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150
                }
            }
        ],
        "metadata": {
            "session_id": "sess_789",
            "user_preferences": {
                "language": "en",
                "format": "markdown",
                "verbosity": "detailed"
            }
        }
    }

    pretty_print_json(complex_structure, "Complex LLM Response Structure")

    print("\n✅ Pretty printing demonstration complete!")
    print("\nAvailable functions:")
    print("- pretty_print_response(): For LLM response objects")
    print("- pretty_print_json(): For JSON data")
    print("- pretty_print_dict(): For dictionaries")
    print("- pretty_print_list(): For lists")
    print("- pretty_print_messages(): For chat conversations")
    print("- pretty_print_tokens_usage(): For token usage info")
    print("- pp(): Quick debug printing")

if __name__ == "__main__":
    demo_pretty_printing()
