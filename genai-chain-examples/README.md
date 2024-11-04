## GenAI Chain Examples

This repository contains some examples of GenAI chains. Check the readme of each chain for more information.

* [Chain Echo](genai_chain_echo/README.md): This chain returns the input string.
* [Chain Joke](genai_chain_joke/README.md): Calls the OpenAI Chat to generate a joke.
* [Chain Auth](genai_chain_auth/README.md): This chain returns the authorization information.
* [Chain Metrics](genai_chain_metrics/README.md): This chain publish a custom Prometheus metric.
* [Chain Gateway](genai_chain_gateway/README.md): Calls the OpenAI Chat through a gateway to generate a joke.
* [Chain Memory](genai_chain_memory/README.md): This chain mantains a conversation with local persisted memory.

## Deployment

### Deploy in local

1. Execute `docker-compose up -d` to start the services.
2. Execute `scripts/load_vault_secrets.py` to load the secrets in Vault.
3. Execute `scripts/create_openai_endpoints.py` to create the OpenAI endpoints in GenAI Gateway.
4. Run the Chain:
   * Execute `main.py` in PyCharm.
   * Or execute `poetry run start_<chain>` or `python main.py` in a terminal.
   * Or load the chain in GenAI API server: http://127.0.0.1:8081
5. Test the chain:
   * Execute `tests/test_chain.py` in PyCharm.
   * Or execute `poetry run pytest` in a terminal.

Services in docker-compose:

* GenAI API URL: http://127.0.0.1:8081
* GenAI Gateway URL: http://127.0.0.1:8082
* Vault URL: http://127.0.0.1:8200
* Vault token: root-token

To stop the services:

1. Execute `docker-compose down` to stop the services.
2. Execute `docker-compose down -v` to remove the persistent data.

### Configure the secrets in Vault

Configure the OpenAI token:

* Engine: userland
* Path: /passwords/genai-api.s000001-genai/openai-token
* Secret data:
  * token = `<openai-token>`

NOTE: To deploy in a Stratio environment you have to replace "genai-api.s000001-genai" in the path with the name of the service.
