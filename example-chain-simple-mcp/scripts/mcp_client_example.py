"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

"""Example MCP client that calls the tools exposed by SimpleMcpChain.

Prerequisites:
  1. The chain must be running locally:
       poetry run python simple_mcp_chain/main.py

  2. Run this script from the example directory:
       poetry run python scripts/mcp_client_example.py
"""

import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

MCP_URL = "http://127.0.0.1:8080/mcp"

# Auth metadata passed as MCP request _meta.
# Locally the server falls back to env vars if this is omitted, but the
# platform always injects proper auth in production.
AUTH_META = {
    "genai_state": {
        "client_auth_type": "mtls",
        "client_user_id": "local-dev-user",
        "client_tenant": "local-tenant",
        "client_role": "consumer",
    }
}


async def main() -> None:
    print(f"Connecting to MCP server at {MCP_URL}\n")

    async with Client(StreamableHttpTransport(MCP_URL)) as client:

        # ------------------------------------------------------------------
        # Discover available tools
        # ------------------------------------------------------------------
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        print()

        # ------------------------------------------------------------------
        # Call get_current_time (no user arguments)
        # ------------------------------------------------------------------
        print("Calling get_current_time ...")
        result = await client.call_tool("get_current_time", {}, meta=AUTH_META)
        if result.is_error:
            print(f"  ERROR: {result.structured_content}")
        else:
            print(f"  time:     {result.structured_content['time']}")
            print(f"  timezone: {result.structured_content['timezone']}")
        print()

        # ------------------------------------------------------------------
        # Call format_text with each supported style
        # ------------------------------------------------------------------
        sample_text = "hello mcp world"
        for style in ("upper", "lower", "title", "reverse"):
            print(f"Calling format_text(text={sample_text!r}, style={style!r}) ...")
            result = await client.call_tool(
                "format_text",
                {"text": sample_text, "style": style},
                meta=AUTH_META,
            )
            if result.is_error:
                print(f"  ERROR: {result.structured_content}")
            else:
                print(f"  result: {result.structured_content['result']}")
        print()

        # ------------------------------------------------------------------
        # Call analyze_text — delegates to chain.chain().invoke()
        # ------------------------------------------------------------------
        print("Calling analyze_text (delegates to chain invoke) ...")
        result = await client.call_tool(
            "analyze_text",
            {"text": sample_text},
            meta=AUTH_META,
        )
        if result.is_error:
            print(f"  ERROR: {result.structured_content}")
        else:
            print(f"  word_count: {result.structured_content['word_count']}")
            print(f"  char_count: {result.structured_content['char_count']}")
        print()

        print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
