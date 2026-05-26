"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import FastMCPTransport

from simple_mcp_chain.chain import SimpleMcpChain


@pytest.fixture
def mcp_server() -> FastMCP:
    """Build an in-memory FastMCP server with tools registered from SimpleMcpChain."""
    mcp = FastMCP("simple-mcp-chain-test")
    chain = SimpleMcpChain()
    chain.mcp_server(mcp)
    return mcp


@pytest.fixture(autouse=True)
def setup_auth_env(monkeypatch):
    """Provide auth env vars so mcp_tool_wrapper can extract role metadata.

    In production the Stratio GenAI API injects this automatically via the MCP
    request _meta field. Locally and in unit tests env vars are the fallback.
    """
    monkeypatch.setenv("GENAI_METADATA_USER_ID", "test-user")
    monkeypatch.setenv("GENAI_METADATA_TENANT", "test-tenant")
    monkeypatch.setenv("GENAI_METADATA_ROLE", "consumer")


class TestMcpEndpointTools:
    """Integration tests that call MCP tools through FastMCPTransport (in-memory).

    FastMCPTransport connects the Client directly to the FastMCP server in the
    same process without any HTTP server. The protocol path is identical to
    calling the live /mcp endpoint, making these tests suitable for verifying
    tool registration, argument handling, and response shapes.
    """

    @pytest.mark.asyncio
    async def test_list_tools_exposes_expected_tools(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            tools = await client.list_tools()
            tool_names = {t.name for t in tools}
            assert "get_current_time" in tool_names
            assert "format_text" in tool_names

    @pytest.mark.asyncio
    async def test_get_current_time_returns_utc_time(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool("get_current_time", {})
            assert not result.is_error
            assert result.structured_content is not None
            assert "time" in result.structured_content
            assert result.structured_content.get("timezone") == "UTC"

    @pytest.mark.asyncio
    async def test_format_text_upper(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool(
                "format_text", {"text": "hello world", "style": "upper"}
            )
            assert not result.is_error
            assert result.structured_content["result"] == "HELLO WORLD"
            assert result.structured_content["style"] == "upper"

    @pytest.mark.asyncio
    async def test_format_text_lower(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool(
                "format_text", {"text": "HELLO WORLD", "style": "lower"}
            )
            assert result.structured_content["result"] == "hello world"

    @pytest.mark.asyncio
    async def test_format_text_title(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool(
                "format_text", {"text": "hello world", "style": "title"}
            )
            assert result.structured_content["result"] == "Hello World"

    @pytest.mark.asyncio
    async def test_format_text_reverse(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool(
                "format_text", {"text": "hello", "style": "reverse"}
            )
            assert result.structured_content["result"] == "olleh"

    @pytest.mark.asyncio
    async def test_format_text_default_style_is_upper(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool("format_text", {"text": "hello"})
            assert result.structured_content["result"] == "HELLO"

    @pytest.mark.asyncio
    async def test_analyze_text_calls_chain_invoke(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool("analyze_text", {"text": "hello world"})
            assert not result.is_error
            assert result.structured_content["word_count"] == 2
            assert result.structured_content["char_count"] == 11
            assert result.structured_content["text"] == "hello world"

    @pytest.mark.asyncio
    async def test_analyze_text_empty_string(self, mcp_server):
        async with Client(FastMCPTransport(mcp_server)) as client:
            result = await client.call_tool("analyze_text", {"text": ""})
            assert result.structured_content["word_count"] == 0
            assert result.structured_content["char_count"] == 0
