"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

from genai_core.server.server import GenAiServer


def main(chain_config):
    """
    Starts a stand-alone GenAI-api-like server with the chain loaded.

    This chain does not require a Stratio GenAI LiteLLM connection because
    neither the invoke endpoint nor the MCP tools call an LLM. You can run
    it locally without any additional infrastructure.

    Invoke endpoint example body (POST /invoke):
    ```json
    {
      "input": {
        "text": "Hello, MCP world!"
      },
      "config": {
        "metadata": {
          "__genai_state": {
            "client_auth_type": "mtls",
            "client_user_id": "<your-user>",
            "client_tenant": "<your-tenant>"
          }
        }
      }
    }
    ```

    MCP tools available at /mcp (SSE) or /mcp/messages (JSON-RPC):
    - get_current_time: returns the current UTC date and time.
    - format_text: formats a string (upper / lower / title / reverse).
    """
    app = GenAiServer(
        module_name="simple_mcp_chain.chain",
        class_name="SimpleMcpChain",
        config=chain_config,
    )
    app.start_server()


if __name__ == "__main__":
    # This chain requires no external services, so chain_config can be empty.
    chain_config = {}
    main(chain_config)
