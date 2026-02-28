"""
Ultimate Gemini MCP Server

A production-ready MCP server for Google's Gemini 3.1 Flash Image, featuring
high-resolution output (512px-4K), reference images, Google Search grounding,
thinking mode, prompt enhancement, and batch processing.
"""

__version__ = "6.0.2"
__author__ = "Ultimate Gemini MCP"

from .config import get_settings
from .server import create_app, main

__all__ = ["create_app", "main", "get_settings", "__version__"]
