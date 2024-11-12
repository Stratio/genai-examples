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
        module_name="opensearch_chain_example.chain",
        class_name="OpensourceChain",
        config={
            # Change the endpoint according to the model you will use
            "opensearch_url": os.getenv("OPENSEARCH_URL"),
            "opensearch_min_score": 30,
        },
    )
    app.start_server()


if __name__ == "__main__":
    """
    Before running this script, you should configure the following environment variables:
    variables needed to tell the VaulClient where to find the certificates so it does not need to
    actually access any Vault. You can obtain your certificates from your profile in Gosec
    VAULT_LOCAL_CLIENT_CERT=/path/to/cert.crt
    VAULT_LOCAL_CLIENT_KEY=/path/to/private-key.key
    VAULT_LOCAL_CA_CERTS=/path/to/ca-cert.crt

    Opensearch service URL
    OPENSEARCH_URL=https://opensearch.s000001-genai.k8s.fifteen.labs.stratio.com:9200

    GenAI API service name
    GENAI_API_SERVICE_NAME=genai-api-qa3.s000001-genai
    """
    main()
