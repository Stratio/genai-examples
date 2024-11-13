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


def main():
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
                "client_user_id": "Alice",
                "client_tenant": "s000001"
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
        module_name="basic_actor_chain_example.chain",
        class_name="BasicActorChain",
        config={
            # Change the endpoint according to the model you will use
            "gateway_endpoint": "QA-openai-chat-gpt-4o-mini",
            "llm_timeout": 30,
        },
    )
    app.start_server()


if __name__ == "__main__":
    # Before running this script, you should configure the following environment variables:
    # 1. Variables needed to access the Genai-Gateway (here we show an example with):
    # GENAI_GATEWAY_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/genai-gateway
    # GENAI_GATEWAY_CLIENT_CERT=/path/to/user-cert.crt
    # GENAI_GATEWAY_CLIENT_KEY=/path/to/user_private.key
    # GENAI_GATEWAY_CA_CERTS=/path/to/ca-cert.crt
    main()
