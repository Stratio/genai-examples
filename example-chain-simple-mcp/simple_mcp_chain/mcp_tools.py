"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal, Optional

from fastmcp import FastMCP
from genai_core.model.mcp_models import McpToolResponse
from genai_core.runnables.genai_auth import MCP_READ_ROLES
from genai_core.runnables.genai_metadata import GenAiMetadata
from genai_core.runnables.mcp_tool_wrapper import mcp_tool_wrapper

if TYPE_CHECKING:
    from .chain import SimpleMcpChain


class GetCurrentTimeResponse(McpToolResponse):
    """Response for the get_current_time MCP tool."""

    time: Optional[str] = None
    timezone: Optional[str] = None


class FormatTextResponse(McpToolResponse):
    """Response for the format_text MCP tool."""

    result: Optional[str] = None
    style: Optional[str] = None


class AnalyzeTextResponse(McpToolResponse):
    """Response for the analyze_text MCP tool."""

    text: Optional[str] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None


def configure_mcp_tools(mcp: FastMCP, chain: "SimpleMcpChain") -> None:
    """Register all MCP tools on the given FastMCP instance.

    Args:
        mcp: The FastMCP server instance to register tools on.
        chain: The SimpleMcpChain instance used by analyze_text to delegate
            to the chain's invoke logic.
    """

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        }
    )
    @mcp_tool_wrapper("get_current_time", allowed_roles=MCP_READ_ROLES)
    def get_current_time(
        metadata: GenAiMetadata,
    ) -> GetCurrentTimeResponse:
        """Returns the current UTC date and time in ISO 8601 format."""
        now = datetime.now(timezone.utc)
        return GetCurrentTimeResponse(
            time=now.isoformat(),
            timezone="UTC",
        )

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        }
    )
    @mcp_tool_wrapper("format_text", allowed_roles=MCP_READ_ROLES)
    def format_text(
        metadata: GenAiMetadata,
        text: str,
        style: Literal["upper", "lower", "title", "reverse"] = "upper",
    ) -> FormatTextResponse:
        """Formats the given text according to the specified style.

        Args:
            text: The input text to format.
            style: Transformation to apply. One of:
                - "upper": convert to uppercase.
                - "lower": convert to lowercase.
                - "title": capitalize each word.
                - "reverse": reverse the character order.
        """
        formatters = {
            "upper": str.upper,
            "lower": str.lower,
            "title": str.title,
            "reverse": lambda t: t[::-1],
        }
        return FormatTextResponse(result=formatters[style](text), style=style)

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
        }
    )
    @mcp_tool_wrapper("analyze_text", allowed_roles=MCP_READ_ROLES)
    def analyze_text(
        metadata: GenAiMetadata,
        text: str,
    ) -> AnalyzeTextResponse:
        """Returns word count and character count for the given text.

        Delegates to the chain's invoke logic.

        Args:
            text: The input text to analyze.
        """
        result = chain.chain().invoke({"text": text})
        return AnalyzeTextResponse(
            text=result["text"],
            word_count=result["word_count"],
            char_count=result["char_count"],
        )
