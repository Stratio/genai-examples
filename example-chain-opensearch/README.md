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

We assume that you already have poetry installed. If not, you can install it wit:
```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry --version
```

Verify that you have a dependencies source in your `pyproject.toml` with the URL of the PyPi server in 
genai-developer-proxy (or the one in gena-api) providing the needed stratio packages, like genai-core. 
Note that the URL below is just an example and you should add the correct URL for your case.
```toml
[[tool.poetry.source]]
name = "stratio-releases"
url = "https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/v1/pypi/simple/"
priority = "supplemental"
```
You should also configure Poetry to use the CA of the cluster to verify the certificate of the
above configured repository (the CA of the cluster can be found in the zip you obtain from Gosec with your
certificates).

```
$ poetry config certificates.stratio-releases.cert /path/to/ca-cert.crt 
```

Then install the poetry environment:
```
$ poetry install
```

Set up the needed environment variables. You can create a file `env.sh` like the following:

```bash
# variables needed to tell the VaulClient where to find the certificates so it does not need to
# actually access any Vault. You can obtain your certificates from your profile in Gosec
export VAULT_LOCAL_CLIENT_CERT="/path/to/cert.crt"
export VAULT_LOCAL_CLIENT_KEY="/path/to/private-key.key"
export VAULT_LOCAL_CA_CERTS="/path/to/ca-cert.crt"

export OPENSEARCH_URL="https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/opensearch"
```

You need to specify the Opensearch that the chain will connect to. 
This is normally specified in the deployment configuration of the chain when registering it in *Stratio GenAI API*. 
While developing locally, you run your chain in a standalone server which is started by running the the `main.py` script. 
This scripts obtains the Opensearch URL from the `OPENSEARCH_URL` environment variable, so you should set it with correct value before starting the chain. 
If accessing Opensearch through the *Stratio GenAI Developer Proxy*, it would be something like:

```
$ OPENSEARCH_URL="https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/opensearch"
```

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment

```
$ poetry run python opensearch_chain/main.py
```

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

In case you want to debug the chain, you can run it in PyCharm as explained in the main [README.md](../README.md) file.

The `"config"` key with the extra metadata is normally added by GenAI API before passing the input to the chain,
but while developing locally you should add it by hand.