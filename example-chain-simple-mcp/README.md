# Example Chain with a Simple MCP Server

This example shows how to embed an **MCP (Model Context Protocol) server** in a GenAI chain. The chain exposes two utility tools that AI assistants and other MCP-compatible clients can call directly, without going through the chain's main invoke endpoint.

This example is the practical counterpart of the MCP server section in the [GenAI Core developer guide](https://github.com/Stratio/genai-core/pull/688).

## What this example demonstrates

- Overriding `mcp_server()` from `BaseGenAiChain` to embed an MCP server.
- Registering MCP tools with `@mcp.tool()` and `@mcp_tool_wrapper()`.
- Using `MCP_READ_ROLES` for role-based access control on MCP tools.
- Defining typed MCP tool responses extending `McpToolResponse`.
- Structuring tool registration in a dedicated `mcp_tools.py` module.

### MCP tools exposed

| Tool | Calls chain? | Description |
|---|---|---|
| `get_current_time` | No | Returns the current UTC date and time in ISO 8601 format. |
| `format_text` | No | Formats a string: `upper`, `lower`, `title`, or `reverse`. |
| `analyze_text` | **Yes** | Returns word count and character count by delegating to `chain.chain().invoke()`. |

`get_current_time` and `format_text` are pure utility functions independent of the chain logic.
`analyze_text` shows the pattern of calling the chain from an MCP tool.

## Local deployment

To set up the chain locally, follow the steps in the [main README of this repository](../README.md). Here is a summary:

1. Make sure you have Python >= 3.11 and Poetry >= 2.2 installed.

2. Edit `pyproject.toml` and set the `stratio-releases` repository URL to your *Stratio GenAI Developer Proxy* Load Balancer:

```toml
[[tool.poetry.source]]
name = "stratio-releases"
url = "https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-api/v1/pypi/simple/"
priority = "supplemental"
```

3. Install dependencies:

```bash
poetry config virtualenvs.in-project true
poetry config certificates.stratio-releases.cert /path/to/your/cert/folder/ca-cert.crt
poetry lock
poetry install
```

4. Run the chain (no LiteLLM connection needed for this example):

```bash
poetry run python simple_mcp_chain/main.py
```

Open the Swagger UI at `http://127.0.0.1:8080/`.

### Invoke endpoint

Call `POST /invoke` with:

```json
{
  "input": {
    "text": "Hello, MCP world!"
  }
}
```

Expected response:

```json
{
  "output": {
    "text": "Hello, MCP world!",
    "word_count": 3,
    "char_count": 18
  }
}
```

### MCP tools

The MCP server is mounted at `http://127.0.0.1:8080/mcp` using the [Streamable HTTP transport](https://modelcontextprotocol.io/docs/concepts/transports).

#### Python client (recommended)

Use the `fastmcp` library (already a transitive dependency of `genai-core`):

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

MCP_URL = "http://127.0.0.1:8080/mcp"

# Auth metadata required by the Stratio GenAI platform.
# Locally the server accepts any role; in production this is injected automatically.
AUTH_META = {
    "genai_state": {
        "client_auth_type": "mtls",
        "client_user_id": "<your-user>",
        "client_tenant": "<your-tenant>",
        "client_role": "consumer",
    }
}

async def main():
    async with Client(StreamableHttpTransport(MCP_URL)) as client:

        # Discover available tools
        tools = await client.list_tools()
        print([t.name for t in tools])
        # ['get_current_time', 'format_text']

        # Call get_current_time (no arguments)
        result = await client.call_tool("get_current_time", {}, meta=AUTH_META)
        print(result.structured_content)
        # {'time': '2025-05-26T10:30:00.123456+00:00', 'timezone': 'UTC'}

        # Call format_text
        result = await client.call_tool(
            "format_text",
            {"text": "hello world", "style": "title"},
            meta=AUTH_META,
        )
        print(result.structured_content)
        # {'result': 'Hello World', 'style': 'title'}

asyncio.run(main())
```

A ready-to-run version of this script is available at [`scripts/mcp_client_example.py`](scripts/mcp_client_example.py).

#### Raw JSON-RPC (curl)

The MCP Streamable HTTP transport uses JSON-RPC 2.0 over HTTP POST. It requires
**session management**: the server returns an `mcp-session-id` header on `initialize`,
and every subsequent request must include that header. Responses arrive as
Server-Sent Events (`event: message\ndata: {...}`).

The Python client handles all of this automatically. Use curl only for debugging.

```bash
# Step 1 — initialize and capture the session ID
SESSION_ID=$(curl -s -i -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}' \
  | grep -i "mcp-session-id" | tr -d '\r' | awk -F': ' '{print $2}')

echo "Session: $SESSION_ID"

# Step 2 — send the required initialized notification (no response expected)
curl -s -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'

# Step 3 — list available tools
curl -s -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# Step 4 — call get_current_time (no user arguments)
curl -s -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_current_time","arguments":{},"_meta":{"genai_state":{"client_user_id":"<your-user>","client_tenant":"<your-tenant>","client_role":"consumer"}}}}'

# Step 5 — call format_text with arguments
curl -s -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"format_text","arguments":{"text":"hello world","style":"title"},"_meta":{"genai_state":{"client_user_id":"<your-user>","client_tenant":"<your-tenant>","client_role":"consumer"}}}}'
```

Expected SSE response for `format_text`:

```
event: message
data: {"jsonrpc":"2.0","id":4,"result":{"content":[{"type":"text","text":"{\"result\":\"Hello World\",\"style\":\"title\"}"}],"structuredContent":{"result":"Hello World","style":"title"},"isError":false}}
```

> **Note**: the `_meta.genai_state.client_role` field is required by `mcp_tool_wrapper`
> for role-based access control. Without it the tool returns
> `{"error": "Access denied: user role not provided in request metadata."}`.
> The Python client passes this via the `meta=` argument to `call_tool()`.

## Deployment in Stratio GenAI API

1. Build the chain package:

```bash
poetry build
```

2. Open the Swagger UI of the Stratio GenAI API installed in your development environment.

3. Upload the package with `POST /v1/packages`.

4. Deploy the chain with `POST /v1/chains`:

```json
{
  "chain_id": "simple_mcp_chain",
  "chain_config": {
    "package_id": "simple_mcp_chain-0.7.0a0",
    "chain_module": "simple_mcp_chain.chain",
    "chain_class": "SimpleMcpChain",
    "chain_params": {}
  }
}
```

Once deployed, Stratio GenAI API automatically registers the embedded MCP server as a tool provider in Stratio GenAI LiteLLM, making `get_current_time` and `format_text` available for other applications.

5. Invoke the chain with `POST /v1/chains/simple_mcp_chain/invoke`:

```json
{
  "input": {
    "text": "Hello from GenAI API!"
  }
}
```
