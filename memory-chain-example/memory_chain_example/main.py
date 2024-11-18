"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

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
    Starts a stand-alone GenAI-api-like server with the chain loaded so that in can be easily executed locally.
    Note that the chain will need access to a Genai-Gateway server, which could be provided from your
    local machine via the GenAI development proxy. An example of json body to send in invoke POST is
    Start a conversation
    ```json
        {
          "input": {
            "topic": "Sicily",
            "input": "when to go?"
          },
          "config": {
            "metadata": {
              "__genai_state": {
                "client_auth_type": "mtls",
                "client_user_id": "your-user",
                "client_tenant": "your-tenant"
              }
            }
          }
        }
    ```
    Continue a conversation
    ```json
        {
          "input": {
            "topic": "Sicily",
            "input": "can you repeat it?",
            "chat_id": "<chat_id_returned_by_memory_chat_service>"
          },
          "config": {
            "metadata": {
              "__genai_state": {
                "client_auth_type": "mtls",
                "client_user_id": "your-user",
                "client_tenant": "your-tenant"
              }
            },
          }
        }
    ```

    The "config" -> "metadata" -> "__genai_state" is only needed to test while developing locally.
      In a real environment GenAI API adds automatically that fields from the auth info before
      passing the data to the chain
    """
    app = GenAiServer(
        module_name="memory_chain_example.chain",
        class_name="MemoryChain",
        config=chain_config,
    )
    app.start_server()


if __name__ == "__main__":
    # Before running this script, refer to the README.md file to know how to set up
    # your environment correctly in order to communicate with the Stratio GenAI Gateway.
    # The following environment variables should be set:
    # - GENAI_API_SERVICE_NAME=genai-api-service-name.your-tenant-genai
    # - GENAI_API_TENANT=your-tenant
    # - GENAI_API_REST_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-api
    # - GENAI_API_REST_USE_SSL=true
    # - GENAI_API_REST_CLIENT_CERT=/path/to/certs/user.crt
    # - GENAI_API_REST_CLIENT_KEY=/path/to/certs/user_private.key
    # - GENAI_API_REST_CA_CERTS=/path/to/certs/ca-cert.crt
    #
    # - GENAI_GATEWAY_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-gateway
    # - GENAI_GATEWAY_USE_SSL=true
    # - GENAI_GATEWAY_CLIENT_CERT=/path/to/certs/user.crt
    # - GENAI_GATEWAY_CLIENT_KEY=/path/to/certs/user_private.key
    # - GENAI_GATEWAY_CA_CERTS=/path/to/certs/ca-cert.crt
    chain_config = {
        # Change the endpoint according to the model you will use
        "gateway_endpoint": "QA-openai-chat-gpt-4o-mini",
    }
    main(chain_config)
