#!/usr/bin/env python3
"""
Fix for Pydantic serialization warnings in LiteLLM.

The issue occurs because the Message and StreamingChoices classes conditionally
delete optional fields, causing a mismatch between expected and actual field counts
during Pydantic serialization.
"""

import sys
import os
from pathlib import Path

def fix_message_class():
    """
    Fix the Message class to avoid Pydantic serialization warnings.
    """
    utils_path = Path("lib/python3.12/site-packages/litellm/types/utils.py")

    if not utils_path.exists():
        print(f"Error: {utils_path} not found")
        return False

    # Read the current file
    with open(utils_path, 'r') as f:
        content = f.read()

    # Find the Message class __init__ method and fix the field deletion logic
    old_deletion_pattern = '''        if audio is None:
            # delete audio from self
            # OpenAI compatible APIs like mistral API will raise an error if audio is passed in
            if hasattr(self, "audio"):
                del self.audio

        if annotations is None:
            # ensure default response matches OpenAI spec
            # Some OpenAI compatible APIs raise an error if annotations are passed in
            if hasattr(self, "annotations"):
                del self.annotations

        if reasoning_content is None:
            # ensure default response matches OpenAI spec
            if hasattr(self, "reasoning_content"):
                del self.reasoning_content

        if thinking_blocks is None:
            # ensure default response matches OpenAI spec
            if hasattr(self, "thinking_blocks"):
                del self.thinking_blocks'''

    # Replace with a more Pydantic-friendly approach
    new_deletion_pattern = '''        # Set fields to None instead of deleting them to maintain Pydantic schema consistency
        if audio is None:
            # OpenAI compatible APIs like mistral API will raise an error if audio is passed in
            self.audio = None

        if annotations is None:
            # ensure default response matches OpenAI spec
            # Some OpenAI compatible APIs raise an error if annotations are passed in
            self.annotations = None

        if reasoning_content is None:
            # ensure default response matches OpenAI spec
            self.reasoning_content = None

        if thinking_blocks is None:
            # ensure default response matches OpenAI spec
            self.thinking_blocks = None'''

    if old_deletion_pattern in content:
        content = content.replace(old_deletion_pattern, new_deletion_pattern)
        print("✓ Fixed Message class field deletion logic")
    else:
        print("⚠ Message class deletion pattern not found - may already be fixed or pattern changed")

    # Also fix the Delta class similar deletion logic
    old_delta_pattern = '''        if reasoning_content is not None:
            self.reasoning_content = reasoning_content
        else:
            # ensure default response matches OpenAI spec
            del self.reasoning_content

        if thinking_blocks is not None:
            self.thinking_blocks = thinking_blocks
        else:
            # ensure default response matches OpenAI spec
            del self.thinking_blocks

        # Add annotations to the delta, ensure they are only on Delta if they exist (Match OpenAI spec)
        if annotations is not None:
            self.annotations = annotations
        else:
            del self.annotations'''

    new_delta_pattern = '''        if reasoning_content is not None:
            self.reasoning_content = reasoning_content
        else:
            # ensure default response matches OpenAI spec
            self.reasoning_content = None

        if thinking_blocks is not None:
            self.thinking_blocks = thinking_blocks
        else:
            # ensure default response matches OpenAI spec
            self.thinking_blocks = None

        # Add annotations to the delta, ensure they are only on Delta if they exist (Match OpenAI spec)
        if annotations is not None:
            self.annotations = annotations
        else:
            self.annotations = None'''

    if old_delta_pattern in content:
        content = content.replace(old_delta_pattern, new_delta_pattern)
        print("✓ Fixed Delta class field deletion logic")
    else:
        print("⚠ Delta class deletion pattern not found - may already be fixed or pattern changed")

    # Write the fixed content back
    with open(utils_path, 'w') as f:
        f.write(content)

    return True

def fix_choices_class():
    """
    Fix the Choices class to avoid Pydantic serialization warnings.
    """
    utils_path = Path("lib/python3.12/site-packages/litellm/types/utils.py")

    if not utils_path.exists():
        print(f"Error: {utils_path} not found")
        return False

    # Read the current file
    with open(utils_path, 'r') as f:
        content = f.read()

    # Find and fix the Choices class deletion logic
    old_choices_pattern = '''        if self.logprobs is None:
            del self.logprobs
        if self.provider_specific_fields is None:
            del self.provider_specific_fields'''

    new_choices_pattern = '''        # Keep fields as None instead of deleting for Pydantic consistency
        # if self.logprobs is None:
        #     del self.logprobs
        # if self.provider_specific_fields is None:
        #     del self.provider_specific_fields'''

    if old_choices_pattern in content:
        content = content.replace(old_choices_pattern, new_choices_pattern)
        print("✓ Fixed Choices class field deletion logic")
    else:
        print("⚠ Choices class deletion pattern not found - may already be fixed or pattern changed")

    # Write the fixed content back
    with open(utils_path, 'w') as f:
        f.write(content)

    return True

def main():
    """
    Main function to apply the fixes.
    """
    print("🔧 Fixing Pydantic serialization warnings in LiteLLM...")
    print()

    # Check if we're in the right directory
    if not Path("lib/python3.12/site-packages/litellm").exists():
        print("❌ Error: LiteLLM package not found in expected location")
        print("   Make sure you're running this from the project root directory")
        return 1

    success = True

    # Apply fixes
    if not fix_message_class():
        success = False

    if not fix_choices_class():
        success = False

    if success:
        print()
        print("✅ Successfully applied fixes for Pydantic serialization warnings!")
        print()
        print("The fixes change the field deletion logic to set fields to None instead")
        print("of deleting them, which maintains Pydantic schema consistency.")
        print()
        print("You can now run your LiteLLM code without the serialization warnings.")
    else:
        print()
        print("❌ Some fixes could not be applied. Please check the error messages above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
