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
    Note that the chain will need access to a OpenSearch server, which should be accessible from your local machine.
    The OpenSearchService class provided in this example is a simple service to interact with an OpenSearch instance
     and should be adapted to your specific use case.
    The url of the OpenSearch instance should be provided in the OPENSEARCH_URL environment variable (see README.md for more information).
    An example of json body that work with our sample chain, to send in invoke POST is
    ```json
        {
           "input": {
              "search_value":"Scott",
              "collection_name":"semantic_banking_customer_product360",
              "table_value":"customer",
              "column_value":"Full_Name"
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
        module_name="opensearch_chain.chain",
        class_name="OpenSearchChain",
        config={
            # OPENSEARCH_URL environment variable need to be set
            # with the OpenSearch service url (see README.me for more information):
            "opensearch_url": os.getenv("OPENSEARCH_URL"),
            "opensearch_min_score": 30,
        },
    )
    app.start_server()


if __name__ == "__main__":
    # Before running this script, refer to the README.md file to know how to set up
    # your environment correctly in order to communicate with the OpenSearch service
    main()
