# Example Chain with OpenSearch service

This is an example of a GenAI chain that connects to Opensearch service and processes the result of a search.

For the specific case of this example chain, we developed an OpenSearch utility service that connects to an OpenSearch service and performs a search on a specific index and table.

In this example, we assume that an external process created the index using the name of the database
and added documents by analyzing the data in the tables and indexing the selected columns with all their possible values, 
creating document with the following fields:

* _table_: the table name,
* _column_: the column name,
* _value_: the value of the column.

The query coded in the service, returns the first documents that matches the search value in a specific table and column.
The chain will present the first of these value as the result of the chain if a result is found.

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
VAULT_LOCAL_CLIENT_CERT=/path/to/certs/user.crt
VAULT_LOCAL_CLIENT_KEY=/path/to/certs/user_private.key
VAULT_LOCAL_CA_CERTS=/path/to/certs/ca-cert.crt
OPENSEARCH_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/opensearch
```

5. Run the chain `opensearch_chain/main.py`. You can do it in the terminal or in PyCharm. You can open the Swagger UI in the URL `http://127.0.0.1:8080/`.

6. Invoke the chain using the `POST /invoke` endpoint with the following request body. Replace `<your-user>` and `<your-tenant>` with your user and tenant:

```json
{
  "input": {
    "search_value": "<value_to_search>",
    "collection_name": "<index_name>",
    "table_value": "<table_name>",
    "column_value": "<column_name>"
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
  "chain_id": "opensearch_chain",
  "chain_config": {
    "package_id": "opensearch_chain-0.3.1a0",
    "chain_module": "opensearch_chain.chain",
    "chain_class": "OpenSearchChain",
    "chain_params": {
      "opensearch_url": "https://opensearch.s000001-datastores:9200",
      "opensearch_min_score": 30
    }
  }
}
```

5. Invoke the chain using the `POST /v1/chains/opensearch_chain/invoke` endpoint with the following request body. You don't need to include your credentials in the metadata, GenAI API will set them automatically:

```json
{
  "input": {
    "search_value": "<value_to_search>",
    "collection_name": "<index_name>",
    "table_value": "<table_name>",
    "column_value": "<column_name>"
  }
}
```
