# Example chain to show how to create a simple Actor and invoke it from the chain

This is an example chain to show how to define a simple actor and use it in a chain

## Local deployment

Verify that you have a dependencies source in your `pyproject.toml` with the url of the pypi server in genai-api
providing the needed stratio packages, like genai-core. Note that the URL below is just an example, and you
should add the correct URL for your case.
```toml
[[tool.poetry.source]]
name = "genai-api-pypi"
url = "https://genai-api-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080/v1/pypi/simple/"
priority = "supplemental"
```
If using an SSL server, you should configure poetry to use the CA of the cluster to verify the certificate of the
above configured repository (the CA of the cluster can be found in the zip you obtain from Gosec with your
certificates)

```
$ poetry config certificates.genai-api-pypi.cert /path/to/ca-cert.crt 
```

Then install the poetry environment
```
$ poetry install
```

Set up the needed environment variables. You can create a file `env.sh` like the following:
```bash
# variables needed to tell the VaulClient where to find the certificates so it does not need to 
# actually access any Vault. You can obtain your certificates from your profile in Gosec
export VAULT_LOCAL_CLIENT_CERT=/path/to/cert.crt
export VAULT_LOCAL_CLIENT_KEY=/path/to/private-key.key
export VAULT_LOCAL_CA_CERTS=/path/to/ca-cert.crt

# Opensearch service URL
export OPENSEARCH_URL=https://opensearch.s000001-genai.k8s.fifteen.labs.stratio.com:9200
```
and then source it (or add to PyCharm)
```
$ source env.sh
```

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment
```
$ poetry run python basic_actor_chain_example/main.py
```
In case you want to run the chain in debug mode, you can run it in PyCharm.

You can test your chain either via the swagger UI exposed by the local chain server, or with curl.
An example of request body for the invoke POST is the following:
```json
{
  "input": {
     "user_request": "Hi! Nice to meet you! Where's the Queen of Hearts?"
  },
  "config": {
    "metadata": {
      "__genai_state": {
        "client_auth_type": "mtls",
        "client_user_id": "Alice",
        "client_tenant": "s000001"
      }
    }
  }
}
```
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