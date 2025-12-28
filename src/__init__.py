"""
Ultimate Gemini MCP Server

A unified MCP server that combines the best features from:
- Gemini 2.5 Flash Image (with prompt enhancement)
- Imagen 3, 4, and 4-Ultra
- Advanced features: batch processing, editing, templates, and more
"""

__version__ = "3.0.14"
__author__ = "Ultimate Gemini MCP"

from .config import get_settings
from .server import create_app, main

__all__ = ["create_app", "main", "get_settings", "__version__"]
