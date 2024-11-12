# Example chain to show how to connect to Virtualizer from the chain

This is an example chain to show how to run queries in Virtualizer from a chain

## Local deployment

Verify that you have a dependencies source in your `pyproject.toml` with the url of the pypi server in genai-api
providing the needed stratio packages, like genai-core. Note that the URL below is just an example and you
should add the correct URL for your case.
```toml
[[tool.poetry.source]]
name = "genai-api-pypi"
url = "https://genai-api-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080/v1/pypi/simple/"
priority = "supplemental"
```
If using a SSL server, you should configure poetry to use the CA of the cluster to verify the certificate of the
above configured repository (the CA of the cluster can be found in the zip you obtain from Gosec with your
certificates)

```
$ poetry config certificates.genai-api-pypi.cert /path/to/ca-cert.crt 
```

Then install the poetry environment
```
$ poetry install
```

Set up the needed environment variables. You can create a file env.sh like the following:
```bash
# 1. Variables needed to access Virtualizer (here we show an example with):
export VIRTUALIZER_HOST="genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com"
export VIRTUALIZER_PORT=8080
# this varialbe is only needed if accessing Virtualizer via the GenAI-development proxy
export VIRTUALIZER_BASE_PATH=/service/virtualizer

# varialbes needed to tell the VaulClient where to find the certificates so it does not need to 
# actually access any Vault. You can obtain your certificates from your profile in Gosec
export VAULT_LOCAL_CLIENT_CERT="/path/to/cert.crt"
export VAULT_LOCAL_CLIENT_KEY="/path/to/private-key.key"
export VAULT_LOCAL_CA_CERTS="/path/to/ca-cert.crt"

# This is needed by the Virtualizer client that the chain uses. Normally this variable is already
# defined when running inside genai-api, but for local development you need to provide it yourself.
# It should match the service name of the GenAI API that your GenAI development proxy is configured to use
export GENAI_API_SERVICE_NAME="genai-api.s000001-genai"
```
and then source it (or add to PyCharm)
```
$ source env.sh
```

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment
```
$ poetry run python virtualizer_chain_example/main.py
```

You can test your chain either via the swagger UI exposed by the local chain server, or with curl.
An example of request body for the invoke POST is the following:
```json
{
  "input": {
     "query": "SELECT 1 as id"
  },
  "config": {
    "metadata": {
      "__genai_state": {
        "client_auth_type": "mtls",
        "client_user_id": "admin",
        "client_tenant": "s000001"
      }
    }
  }
}
```
The `"config"` key with the extra metadata is normally added by GenAI API before passing the input to the chain,
but while developing locally you should add it by hand. Note that the `client_user_id` should the same user as
the one in your cerfificates, otherwise the genai-development will refuse to forward your query to the
Virtualizer server (to make sure that you do not access any data for which you do not have permissions).

