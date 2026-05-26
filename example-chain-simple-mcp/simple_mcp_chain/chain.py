"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

from typing import Optional

from fastmcp import FastMCP
from genai_core.chain.base import BaseGenAiChain
from genai_core.logger.logger import log
from langchain_core.runnables import Runnable, chain

from .mcp_tools import configure_mcp_tools


# This chain demonstrates how to embed an MCP server in a GenAI chain.
# The chain's main invoke endpoint accepts a text input and returns basic
# statistics about it. In addition, the chain exposes two MCP tools
# (get_current_time and format_text) that AI assistants can call directly.
# Neither the invoke endpoint nor the MCP tools require an LLM, which shows
# that MCP tools can be pure utility functions independent of the chain logic.
class SimpleMcpChain(BaseGenAiChain):

    def __init__(self):
        log.info("Preparing Simple MCP Example chain")
        log.info("Simple MCP Example chain ready!")

    def chain(self) -> Runnable:
        """Returns a Runnable that computes basic statistics for the input text.

        Accepts a dict with a ``text`` key and returns a dict with:
        - ``text``: the original input.
        - ``word_count``: number of whitespace-separated words.
        - ``char_count``: total number of characters.
        """

        @chain
        def _process(input_data: dict) -> dict:
            text = input_data.get("text", "")
            return {
                "text": text,
                "word_count": len(text.split()) if text else 0,
                "char_count": len(text),
            }

        return _process

    def mcp_server(self, mcp: FastMCP) -> Optional[FastMCP]:
        """Configures and returns the embedded MCP server.

        Receives the FastMCP instance managed by the framework, registers the
        utility tools defined in mcp_tools.py, and returns it. Returning None
        would disable MCP for this chain.

        Args:
            mcp: The FastMCP server instance provided by the framework.

        Returns:
            The configured FastMCP instance, or None to disable MCP.
        """
        if mcp is None:
            return None
        configure_mcp_tools(mcp, self)
        return mcp
