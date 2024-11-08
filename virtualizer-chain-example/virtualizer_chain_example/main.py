
import os

from genai_core.server.server import GenAiServer


def main():
    """
    Starts a stand-alone GenAI-api-like server with the chain loaded so that in can be easily executed locally.
    Note that the it still needs access to a Virtualizer server, which could be provided from your
    local machine via the GenAI development proxy. An example of json body to send in invoke POST is
    ```json
      {
          "input": {
              "query": "SELECT 1 as id"
          },
          "config": {
              "metadata": {
                  "__genai_state": {
                      "client_auth_type": "mtls",
                      "client_user_id": "admin",
                      "client_tenant": "s000001"
                  }
              }
          }
      }
      ```
      The "config" -> "metadata" -> "__genai_state" is only neede to test while developing locally.
      In a real environamet GenAI API adds automatically that fields from the auth info before
      passing the data to the chain
    """
    app = GenAiServer(
        module_name="virtualizer_chain_example.chain",
        class_name="VirtualizerChain",
        config={
            "virtualizer_host": os.environ["VIRTUALIZER_HOST"],
            "virtualizer_port": int(os.environ["VIRTUALIZER_PORT"])
        },
    )
    app.start_server()



if __name__ == "__main__":
    # # Note that you should configure the following environment variables:
    #
    # # this varialbe is normally already defined inside GenAI api. To try locally we must include it manually
    # os.environ["GENAI_API_SERVICE_NAME"] = "genai-api-test.s000001-genai"
    #
    # # to "bypass" the need of accesing Vault
    # os.environ["VAULT_LOCAL_CLIENT_CERT"] = "path/to/cert.crt"
    # os.environ["VAULT_LOCAL_CLIENT_KEY"] = "/path/to/private.key"
    # os.environ["VAULT_LOCAL_CA_CERTS"] = "/path/to/ca-cert.crt"
    #
    # # Virtualier data
    # os.environ["VIRTUALIZER_HOST"] = "genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com"
    # os.environ["VIRTUALIZER_PORT"] = "8080"
    # # this is needed if accessing virtualizer via the genai-development proxy, but it is not used in the chain
    # os.environ["VIRTUALIZER_BASE_PATH"] = "/service/virtualizer"
    main()
