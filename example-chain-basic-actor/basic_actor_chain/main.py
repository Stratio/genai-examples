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
    ```json
       {
          "input": {
             "user_request": "Hi! Nice to meet you! Where's the Queen of Hearts?"
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
      The "config" -> "metadata" -> "__genai_state" is only needed to test while developing locally.
      In a real environment GenAI API adds automatically that fields from the auth info before
      passing the data to the chain
    """
    app = GenAiServer(
        module_name="basic_actor_chain.chain",
        class_name="BasicActorChain",
        config=chain_config,
    )
    app.start_server()


if __name__ == "__main__":
    # Before running this script, refer to the README.md file to know how to set up
    # your environment correctly in order to communicate with the Stratio GenAI Gateway

    # # GenAI Gateway data (chain config)
    # gateway_endpoint: The ID of the endpoint in the GenAI Gateway pointing to the desired model.
    chain_config = {
        # Change the endpoint according to the model you will use
        "gateway_endpoint": "QA-openai-chat-gpt-4o-mini",
        "llm_timeout": 30,
    }
    main(chain_config)
