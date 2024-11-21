"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import os

from genai_core.server.server import GenAiServer


def main(chain_config):
    """
    Starts a stand-alone GenAI-api-like server with the chain loaded so that in can be easily executed locally.
    Note that it still needs access to a Virtualizer server, which could be provided from your
    local machine via the GenAI developer proxy. An example of json body to send in invoke POST is
    ```json
      {
          "input": {
            "query": "SELECT 1 as id"
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
      The "config" -> "metadata" -> "__genai_state" is only needed to test while developing locally.
      In a real environment GenAI API adds automatically that fields from the auth info before
      passing the data to the chain
    """
    app = GenAiServer(
        module_name="virtualizer_chain.chain",
        class_name="VirtualizerChain",
        config=chain_config,
    )
    app.start_server()


if __name__ == "__main__":
    # # Note that you should configure the following environment variables
    #
    # # this variable is normally already defined inside GenAI api. To try locally we must include it manually
    # os.environ["GENAI_API_SERVICE_NAME"] = "genai-api-test.your-tenant-genai"
    #
    # # to "bypass" the need of accessing Vault
    # os.environ["VAULT_LOCAL_CLIENT_CERT"] = "path/to/cert.crt"
    # os.environ["VAULT_LOCAL_CLIENT_KEY"] = "/path/to/private.key"
    # os.environ["VAULT_LOCAL_CA_CERTS"] = "/path/to/ca-cert.crt"
    #
    # # Virtualizer data (chain config)
    # os.environ["VIRTUALIZER_HOST"] = "genai-developer-proxy-loadbalancer.your-tenant-genai.k8s.yourdomain.com"
    # os.environ["VIRTUALIZER_PORT"] = "8080"
    # # this is needed if accessing virtualizer via the genai-developer-proxy, but it is not used in the chain
    # os.environ["VIRTUALIZER_BASE_PATH"] = "/service/virtualizer"
    chain_config = {
        "virtualizer_host": os.environ["VIRTUALIZER_HOST"],
        "virtualizer_port": int(os.environ["VIRTUALIZER_PORT"]),
    }
    main(chain_config)
