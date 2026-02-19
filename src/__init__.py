"""
Ultimate Gemini MCP Server

A production-ready MCP server for Google's Gemini 3 Pro Image, featuring
high-resolution output (1K-4K), reference images, Google Search grounding,
thinking mode, prompt enhancement, and batch processing.
"""

__version__ = "3.0.18"
__author__ = "Ultimate Gemini MCP"

from .config import get_settings
from .server import create_app, main

__all__ = ["create_app", "main", "get_settings", "__version__"]
