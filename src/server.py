#!/usr/bin/env python3
"""
Gemini 3.1 Flash Image MCP Server - Main Entry Point

Supports Gemini 3.1 Flash Image with 4K resolution, thinking mode, reference images,
Google Search grounding, prompt enhancement, and batch processing.
"""

import logging
import sys

from fastmcp import FastMCP

from .config import ALL_MODELS, get_settings
from .prompts import register_image_prompts
from .tools import register_batch_generate_tool, register_generate_image_tool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP requires stderr for logging, not stdout
)

logger = logging.getLogger(__name__)


def create_app() -> FastMCP:
    """
    Create and configure the Ultimate Gemini MCP application.

    This is the factory function used by FastMCP CLI.
    """
    logger.info("Initializing Ultimate Gemini MCP Server...")

    try:
        settings = get_settings()

        logger.info(f"Output directory: {settings.output_dir}")
        logger.info(f"Prompt enhancement: {settings.api.enable_prompt_enhancement}")
        logger.info(f"Available models: {', '.join(ALL_MODELS.keys())}")

        mcp = FastMCP(
            "Ultimate Gemini MCP",
            version="6.0.2",
        )

        register_generate_image_tool(mcp)
        register_batch_generate_tool(mcp)
        register_image_prompts(mcp)

        logger.info("Ultimate Gemini MCP Server initialized successfully")
        return mcp

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point for direct execution."""
    try:
        logger.info("Starting Ultimate Gemini MCP Server...")
        app = create_app()
        logger.info("Server is ready and listening for MCP requests")

        settings = get_settings()
        # Apply server configuration from settings
        # Only pass host/port for HTTP transport (stdio doesn't accept them)
        transport = settings.server.transport
        if transport == "stdio":
            app.run(transport="stdio")
        elif transport == "sse":
            app.run(transport="sse", host=settings.server.host, port=settings.server.port)
        elif transport == "http" or transport == "streamable-http":
            app.run(transport="http", host=settings.server.host, port=settings.server.port)
        else:
            # Default to stdio for unknown transport
            app.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
