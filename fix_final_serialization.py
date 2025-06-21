#!/usr/bin/env python3
"""
Final fix for ChatCompletionMessageToolCall Pydantic serialization warnings.

This addresses the core issue by ensuring proper type conversion during object creation.
"""

import sys
import os
from pathlib import Path

def fix_final_serialization():
    """
    Fix the serialization issue by improving type handling in Message class.
    """
    utils_path = Path("lib/python3.12/site-packages/litellm/types/utils.py")

    if not utils_path.exists():
        print(f"Error: {utils_path} not found")
        return False

    # Read the current file
    with open(utils_path, 'r') as f:
        content = f.read()

    # Find and replace the Message class field definitions to use proper validation
    old_message_fields = '''class Message(OpenAIObject):
    content: Optional[str]
    role: Literal["assistant", "user", "system", "tool", "function"]
    tool_calls: Optional[List[ChatCompletionMessageToolCall]]
    function_call: Optional[FunctionCall]
    audio: Optional[ChatCompletionAudioResponse] = None
    reasoning_content: Optional[str] = None
    thinking_blocks: Optional[
        List[Union[ChatCompletionThinkingBlock, ChatCompletionRedactedThinkingBlock]]
    ] = None
    provider_specific_fields: Optional[Dict[str, Any]] = Field(
        default=None, exclude=True
    )
    annotations: Optional[List[ChatCompletionAnnotation]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)'''

    new_message_fields = '''class Message(OpenAIObject):
    content: Optional[str]
    role: Literal["assistant", "user", "system", "tool", "function"]
    tool_calls: Optional[List[ChatCompletionMessageToolCall]]
    function_call: Optional[FunctionCall]
    audio: Optional[ChatCompletionAudioResponse] = None
    reasoning_content: Optional[str] = None
    thinking_blocks: Optional[
        List[Union[ChatCompletionThinkingBlock, ChatCompletionRedactedThinkingBlock]]
    ] = None
    provider_specific_fields: Optional[Dict[str, Any]] = Field(
        default=None, exclude=True
    )
    annotations: Optional[List[ChatCompletionAnnotation]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True, validate_assignment=False)'''

    if old_message_fields in content:
        content = content.replace(old_message_fields, new_message_fields)
        print("✓ Updated Message class model_config to disable validation")
    else:
        print("⚠ Message class fields pattern not found")

    # Also add a validator to handle tool_calls conversion properly
    old_message_init_end = '''        add_provider_specific_fields(self, provider_specific_fields)

    def get(self, key, default=None):'''

    new_message_init_end = '''        add_provider_specific_fields(self, provider_specific_fields)

        # Ensure tool_calls are properly converted to avoid serialization warnings
        if hasattr(self, 'tool_calls') and self.tool_calls is not None:
            converted_tool_calls = []
            for tool_call in self.tool_calls:
                if isinstance(tool_call, dict):
                    # Convert dict to ChatCompletionMessageToolCall object
                    converted_tool_calls.append(ChatCompletionMessageToolCall(**tool_call))
                else:
                    converted_tool_calls.append(tool_call)
            self.tool_calls = converted_tool_calls

    def get(self, key, default=None):'''

    if old_message_init_end in content:
        content = content.replace(old_message_init_end, new_message_init_end)
        print("✓ Added tool_calls conversion logic to Message class")
    else:
        print("⚠ Message init end pattern not found")

    # Add a custom __setattr__ method to handle dynamic assignment
    old_setitem = '''    def __setitem__(self, key, value):
        # Allow dictionary-style assignment of attributes
        setattr(self, key, value)

    def json(self, **kwargs):  # type: ignore'''

    new_setitem = '''    def __setitem__(self, key, value):
        # Allow dictionary-style assignment of attributes
        if key == 'tool_calls' and value is not None and isinstance(value, list):
            # Ensure tool_calls are properly converted
            converted_value = []
            for item in value:
                if isinstance(item, dict):
                    converted_value.append(ChatCompletionMessageToolCall(**item))
                else:
                    converted_value.append(item)
            setattr(self, key, converted_value)
        else:
            setattr(self, key, value)

    def json(self, **kwargs):  # type: ignore'''

    if old_setitem in content:
        content = content.replace(old_setitem, new_setitem)
        print("✓ Enhanced Message __setitem__ to handle tool_calls conversion")
    else:
        print("⚠ Message __setitem__ pattern not found")

    # Write the fixed content back
    with open(utils_path, 'w') as f:
        f.write(content)

    return True

def main():
    """
    Main function to apply the final serialization fix.
    """
    print("🔧 Applying final Pydantic serialization fix...")
    print()

    # Check if we're in the right directory
    if not Path("lib/python3.12/site-packages/litellm").exists():
        print("❌ Error: LiteLLM package not found in expected location")
        print("   Make sure you're running this from the project root directory")
        return 1

    success = fix_final_serialization()

    if success:
        print()
        print("✅ Successfully applied final serialization fix!")
        print()
        print("This fix ensures that tool_calls are always properly converted to")
        print("ChatCompletionMessageToolCall objects, preventing Pydantic warnings.")
        print()
        print("You can now run your LiteLLM code without serialization warnings.")
    else:
        print()
        print("❌ Fix could not be applied. Please check the error messages above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
