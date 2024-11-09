### GenAI Chain Gateway

This chain calls the OpenAI Chat through a gateway to generate a joke.

## Local Deployment

### Download dependencies

First of all please update the url with the one provided by your admin in the `pyproject.toml` file.
example: url = "https://genai-api-loadbalancer.s000001-genai.mydomain.com:8080/v1/pypi/simple/"
before running `poetry install`:
`poetry config certificates.genai-api.cert false`
`poetry config virtualenvs.ignore-conda-env true`

then run `poetry install` and you should be able to download the dependencies directly from the genai-api server.

### Deploy in local

First, you must provide the following env variables. If you are using PyCharm you can set those env in your ~/.bashrc
and launch the PyCharm with `pycharm .` in this folder, and they will be automatically added when you run the app.

You can also provide them as Environment variables inside Run Configuration in PyCharm when you run your app.

```bash
GENAI_API_SERVICE_NAME=genai-api-qa1.s000001-genai
GENAI_API_TENANT=s000001

GENAI_API_REST_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/genai-api
GENAI_API_REST_CLIENT_CERT=/home/mleida/Descargas/s000001-user-certs/s000001-user.crt
GENAI_API_REST_CLIENT_KEY=/home/mleida/Descargas/s000001-user-certs/s000001-user_private.key
GENAI_API_REST_CA_CERTS=/home/mleida/Descargas/s000001-user-certs/ca-cert.crt

GENAI_GATEWAY_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/genai-gateway
GENAI_GATEWAY_CLIENT_CERT=/home/mleida/Descargas/s000001-user-certs/s000001-user.crt
GENAI_GATEWAY_CLIENT_KEY=/home/mleida/Descargas/s000001-user-certs/s000001-user_private.key
GENAI_GATEWAY_CA_CERTS=/home/mleida/Descargas/s000001-user-certs/ca-cert.crt

VAULT_LOCAL_CLIENT_CERT=/home/mleida/Descargas/s000001-user-certs/s000001-user.crt
VAULT_LOCAL_CLIENT_KEY=/home/mleida/Descargas/s000001-user-certs/s000001-user_private.key
VAULT_LOCAL_CA_CERTS=/home/mleida/Descargas/s000001-user-certs/ca-cert.crt

VIRTUALIZER_HOST=genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com
VIRTUALIZER_PORT=8080
VIRTUALIZER_BASE_PATH=/service/virtualizer

GOVERNANCE_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/governance/

```

1. Ensure you have the environment variables defined in `Deploy in local`:
2. Run the Chain:
    * Execute `main.py` in PyCharm.
    * Or execute `poetry run start_<chain>` or `python main.py` in a terminal.
    * Or load the chain in GenAI API server: http://127.0.0.1:8081
3. Test the chain:
    * Execute `tests/test_chain.py` in PyCharm.
    * Or execute `poetry run pytest` in a terminal.

### Chain Configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "basic_Actor_chain",
  "chain_config": {
    "package_id": "basic-actor-chain-example-0.1.0a0",
    "chain_module": "basic-actor-chain-example.chain",
    "chain_class": "BasicActorChain",
    "chain_params": {
      "chat_temperature": 0.5,
      "request_timeout": 30, 
      "n": 1,
      "json_format": false
    },
    "worker_config": {
      "log_level": "info",
      "workers": 1,
      "invoke_timeout": 120
    }
  }
}
```

### Invoke input

* `topic`: Topic of the joke.

Example JSON:

```json
{
  "input": {
    "topic": "cars"
  },
  "config": {},
  "kwargs": {}
}
```

### Invoke output

Example JSON:

```json
{
  "output": {
    "content": "Why don't cars make good comedians? \n\nBecause their jokes always run out of gas!",
    "additional_kwargs": {},
    "response_metadata": {},
    "type": "ai", 
    "name": null,
    "id": null,
    "example": false
  },
  "callback_events": [],
  "metadata": {
    "run_id": "256e6683-09ef-4844-9a8d-d6fe64661807"
  }
}
```
