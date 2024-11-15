# Example chain that connects to Opensearch service

This is an example of a GenAI chain that connects to Opensearch service and processes the result of a search.

For the specific case of this example chain, we developed an OpenSearch utility service that connects to an OpenSearch service and performs a search on a specific index and table.

In ths example, we assume that an external process created the index using the name of the database
and added documents by analyzing the data in the tables and indexing the selected columns with all their possible values, 
creating document with the following fields:

* _table_: the table name,
* _column_: the column name,
* _value_: the value of the column.

the query coded in the service, returns the first documents that matches the search value in a specific table and column.
The chain will present the first of these value as the result of the chain if a result is found.

## Local deployment

Please refer to the main [README.md](../README.md) for instructions on how to set up the development environment.

You need to specify the Opensearch that the chain will connect to. This is normally specified in the deployment configuration of the chain when registering it in *Stratio GenAI API*. While developing locally, you run your chain in a standalone server which is started by running the the `main.py` script. This scripts obtains the Opensearch URL from the `OPENSEARCH_URL` environment variable, so you should set it with correct value before starting the chain. If accesssing Opensearch through the *Stratio GenAI Developer Proxy*, it would be something like:
```
$ export OPENSEARCH_URL="https://genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080/service/opensearch"
```
Also, make sure that you have set the environment variables with your certificates so that the Vault client does not try to connect to Vault:
```
$ export VAULT_LOCAL_CLIENT_CERT="/path/to/cert.crt"
$ export VAULT_LOCAL_CLIENT_KEY="/path/to/private-key.key"
$ export VAULT_LOCAL_CA_CERTS="/path/to/ca-cert.crt"
```

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment

```
$ poetry run python opensearch_chain_example/main.py
```

In case you want to debug the chain, you can run it in PyCharm as explained in the main [README.md](../README.md) file.

Once started, the chain will expose a swagger UI in the following URL: `http://0.0.0.0:8080/`.

You can test your chain either via the swagger UI exposed by the local chain server, or with curl.

An example of request body for the invoke POST is the following:

```json
{
   "input": {
      "search_value":"value_to_search",
      "collection_name":"index_name",
      "table_value":"table_name",
      "column_value":"column_name"
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

Note that the values in the example provided should be adapted to the data present in the OpenSearch service.

The `"config"` key with the extra metadata is normally added by GenAI API before passing the input to the chain,
but while developing locally you should add it by hand.

### Run tests

Run in PyCharm:

* Execute the /tests folder. It works in debug mode too.

Run in the terminal:

* Execute `poetry run pytest`
* Only unit test: `poetry run pytest tests/unit`
* Only integration test: `poetry run pytest tests/integration`.

### Code quality

Run in the terminal:

* To format the code execute `poetry run black ./`
* To lint the code execute `poetry run pylint './**/'`
* To check the types execute `poetry run mypy ./`