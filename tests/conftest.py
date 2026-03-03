import sys
from unittest.mock import MagicMock
import types

# Create mock for modules that are not installed to allow importing src.core.validation
def mock_module(name, **attrs):
    if name in sys.modules:
        return sys.modules[name]
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m

# Mock pydantic
mock_module("pydantic", Field=MagicMock())
mock_module("pydantic_settings", BaseSettings=MagicMock, SettingsConfigDict=MagicMock)

# Mock fastmcp
mock_module("fastmcp", FastMCP=MagicMock)

# Mock google-genai
mock_module("google", genai=MagicMock())
mock_module("google.genai", types=MagicMock())
mock_module("google.genai.types", ImageConfig=MagicMock, GenerateContentConfig=MagicMock)

# Mock PIL/Pillow
mock_module("PIL", Image=MagicMock())
mock_module("pillow")
