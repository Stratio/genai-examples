### GenAI Chain Gateway

This chain calls the OpenAI Chat through a gateway to generate a joke.

## Local Deployment

### Deploy in local

First, you must provide the following env variables. If you are using PyCharm you can set those env in your ~/.bashrc
and launch the PyCharm with `pycharm .` in this folder, and they will be automatically added when you run the app.

You can also provide them as Environment variables inside Run Configuration in PyCharm when you run your app.

```bash
GENAI_GATEWAY_CLIENT_CERT=# Path to your client cert. It will be used to connect to gateway
GENAI_GATEWAY_CLIENT_KEY=# Path to your client key. It will be used to connect to gateway
GENAI_GATEWAY_CA_CERTS=# Path to your ca. It will be used to connect to gateway
GENAI_GATEWAY_URL=http://127.0.0.1:8082 # URL to Gateway Service.
```

1. Ensure you have the environment variables defined in `Deploy in local`:
2. Run the Chain:
    * Start tunnel with Gateway Service using `scripts/start_tunnels.sh`. Sets the value of the KUBE_CONFIG variable with the corresponding configuration file.
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
  "chain_id": "chain_gateway",
  "chain_config": {
    "package_id": "genai_chain_examples-0.1.0",
    "chain_module": "genai_chain_gateway.chain",
    "chain_class": "GatewayChain",
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
