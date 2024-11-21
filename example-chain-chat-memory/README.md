# Example Chain with Chat Memory

This is an example of a GenAI chain that allows to remember the previous conversation in order to provide a more personalized experience.

## Local deployment

To set up the chain locally, follow the steps in the [main README of this repository](../README.md). Here is a summary of the steps:

1. Make sure you have Python >= 3.9 and Poetry installed.

2. Edit the `pyproject.toml` and change the URL of the `stratio-releases` repository. You should use the URL of the *Stratio GenAI Developer Proxy* Load Balancer.

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

4. Configure the environment variables executing the script `scripts/create_env_file.py`. You will find the environment variables in the files `genai-env.env` and `genai-env.sh` in the `genai-examples/scripts` folder. This chain uses the following environment variables:

```bash
GENAI_API_SERVICE_NAME=genai-api-test.s000001-genai
GENAI_API_TENANT=s000001
GENAI_API_REST_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com):8080/service/genai-api
GENAI_API_REST_USE_SSL=true
GENAI_API_REST_CLIENT_CERT=/path/to/certs/user.crt
GENAI_API_REST_CLIENT_KEY=/path/to/certs/user_private.key
GENAI_API_REST_CA_CERTS=/path/to/certs/ca-cert.crt
GENAI_GATEWAY_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com):8080/service/genai-gateway
GENAI_GATEWAY_USE_SSL=true
GENAI_GATEWAY_CLIENT_CERT=/path/to/certs/user.crt
GENAI_GATEWAY_CLIENT_KEY=/path/to/certs/user_private.key
GENAI_GATEWAY_CA_CERTS=/path/to/certs/ca-cert.crt
```

5. Run the chain `chat_memory_chain/main.py`. You can do it in the terminal or in PyCharm. You can open the Swagger UI in the URL `http://127.0.0.1:8080/`.

6. Invoke the chain using the `POST /invoke` endpoint with the following request body. Replace `<your-user>` and `<your-tenant>` with your user and tenant:

```json
{
  "input": {
    "destination": "Sicily",
    "input": "When to go?"
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

7. To continue the conversation include the `chat_id` returned in the response of the previous invocation:

```json
{
  "input": {
    "destination": "Sicily",
    "input": "I prefer another season of the year",
    "chat_id": "<chat_id_returned_in_the_response>"
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
    "package_id": "chat_memory_chain-0.3.1a0",
    "chain_module": "chat_memory_chain.chain",
    "chain_class": "MemoryChain",
    "chain_params": {
      "gateway_endpoint": "openai-chat"
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
