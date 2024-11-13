# Example chain that persists the user's conversation for further interactions

This is an example of a GenAI chain that allows to remember the previous conversation in order to provide a more personalized experience.

## Local deployment

The first step in order to execute the chain in you local environment is to obtain the GenAI Developer Proxy URL and your user certificate.
After you have obtained the necessary information, please refer to the main [README.md](../README.md) for instructions on how to set up the development environment.

The OpenSearch service is exposed with the GenAI developer proxy, so the chain can connect to it using the GenAI API.
The Operator that configured the GenAI Developer Proxy should have configured correctly the OpenSearch service and your user should have the correct permissions to access it.
If you have any issue with the connection, please contact the Operator that configured the GenAI Developer Proxy.

Please check that after running the `create_env_file.py` script (see [Readme](../README.md)), the `.env` created contains the following variables:
```
OPENSEARCH_URL
OPENSEARCH_CLIENT_CERT
OPENSEARCH_CLIENT_KEY
OPENSEARCH_CA_CERTS
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
      "search_value":"Scott",
      "collection_name":"semantic_banking_customer_product360",
      "table_value":"customer",
      "column_value":"Full_Name"
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

Note that the values in the example provided should be adapted to the data present in the OpenSearch service and the user should have the correct permissions to access it.

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