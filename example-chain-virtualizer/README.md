# Example Chain with Virtualizer service

This is an example chain to show how to run queries in Virtualizer from a chain.

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
poetry run local-env --certs_path /path/to/certs --developer_proxy_url https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080
```

Please note that the Virtualizer host, when using the *Stratio GenAI Developer Proxy*, should be configured with the value provided by the *Stratio GenAI Developer Proxy*.

5. Run the chain `virtualizer_chain/main.py`. You can do it in the terminal or in PyCharm. You can open the Swagger UI in the URL `http://127.0.0.1:8080/`.

```bash
poetry run python virtualizer_chain/main.py
```

6. Invoke the chain using the `POST /invoke` endpoint with the following request body:

```json
{
  "input": {
     "query": "SELECT 1 as id"
  }
}
```

> The user credentials are automatically injected from the environment variables configured by the `local-env` script in step 4. No need to include them in the request body.

## Deployment in the Stratio GenAI API

To deploy the chain in the Stratio GenAI API, follow the steps in the [main README of this repository](../README.md). Here is a summary of the steps:

1. Build the chain package with the command `poetry build`.
2. Open the Swagger UI of the Stratio GenAI API installed in your development environment.
3. Upload the chain package with the endpoint `POST /v1/packages`.
4. Deploy the chain with the endpoint `POST /v1/chains` and the request body:

```json
{
  "chain_id": "virtualizer_chain",
  "chain_config": {
    "package_id": "virtualizer_chain-0.7.0a0",
    "chain_module": "virtualizer_chain.chain",
    "chain_class": "VirtualizerChain",
    "chain_params": {
      "virtualizer_host": "virtualizer.s000001-apps",
      "virtualizer_port": "13422"
    }
  }
}
```

5. Invoke the chain using the `POST /v1/chains/virtualizer_chain/invoke` endpoint with the following request body. You don't need to include your credentials in the metadata, GenAI API will set them automatically:

```json
{
  "input": {
     "query": "SELECT 1 as id"
  }
}
```
