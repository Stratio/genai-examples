# Example Chain with Chat Memory

This is an example of a GenAI chain that allows to remember the previous conversation in order to provide a more personalized experience.

## Local deployment

To set up the chain locally, follow the steps in the [main README of this repository](../README.md). Here is a summary of the steps:

1. Make sure you have Python >= 3.11 (GenAI-API uses Python 3.12 to deploy the chain) and Poetry >= 2.2 installed.

2. Edit the `pyproject.toml` and change the URL of the `stratio-releases` repository. You should use the URL of the *Stratio GenAI Developer Proxy* Load Balancer including path "/service/genai-api/v1/pypi/simple".

```toml
[[tool.poetry.source]]
name = "stratio-releases"
url = "https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-api/v1/pypi/simple/"
priority = "supplemental"
```

3. Install the dependencies with Poetry. Replace `/path/to/your/cert/folder/ca-cert.crt` with the path to the CA certificate file.

```bash
$ poetry config virtualenvs.in-project true
$ poetry config certificates.stratio-releases.cert /path/to/your/cert/folder/ca-cert.crt
$ poetry lock --no-update
$ poetry install
```

4. Configure the environment variables running the `local-env` Poetry script. You will find the environment variables in the files `.local_env/genai-env.env` and `.local_env/genai-env.sh`.

```bash
poetry run local-env --certs_path /path/to/certs --developer_proxy_url https://genai.your-tenant.yourdomain.com/genai-developer-proxy
```

5. Run the chain `chat_memory_chain/main.py`. You can do it in the terminal or in PyCharm. You can open the Swagger UI in the URL `http://127.0.0.1:8080/`.

```bash
poetry run python chat_memory_chain/main.py 
```

6. Invoke the chain using the `POST /invoke` endpoint with the following request body:

```json
{
  "input": {
    "destination": "Sicily",
    "input": "When to go?"
  }
}
```

> The user credentials are automatically injected from the environment variables configured by the `local-env` script in step 4. No need to include them in the request body.

7. To continue the conversation include the `chat_id` returned in the response of the previous invocation:

```json
{
  "input": {
    "destination": "Sicily",
    "input": "I prefer another season of the year",
    "chat_id": "<chat_id_returned_in_the_response>"
  }
}
```

## Deployment in the Stratio GenAI API

To deploy the chain in the Stratio GenAI API, follow the steps in the [main README of this repository](../README.md). Here is a summary of the steps:

1. Build the chain package with the command `poetry build`.
2. Open the Swagger UI of the Stratio GenAI API installed in your development environment.
3. Upload the chain package with the endpoint `POST /v1/packages`.
4. Deploy the chain with the endpoint `POST /v1/chains` and the request body:

```json
{
  "chain_id": "chat_memory_chain",
  "chain_config": {
    "package_id": "chat_memory_chain-0.7.0a0",
    "chain_module": "chat_memory_chain.chain",
    "chain_class": "MemoryChain",
    "chain_params": {
      "gateway_endpoint": "openai-chat-gpt-4.1-mini"
    }
  }
}
```

5. Invoke the chain using the `POST /v1/chains/chat_memory_chain/invoke` endpoint with the following request body. You don't need to include your credentials in the metadata, GenAI API will set them automatically:

```json
{
  "input": {
    "destination": "Sicily",
    "input": "When to go?"
  }
}
```
