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

Set up the needed environment variables. You can create a file `env.sh` like the following:
```bash
# 1. Variables needed to access Virtualizer (here we show an example with):
export GENAI_API_REST_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/genai-api
export GENAI_API_REST_CLIENT_CERT=/home/mleida/Descargas/s000001-user-certs/s000001-user.crt
export GENAI_API_REST_CLIENT_KEY=/home/mleida/Descargas/s000001-user-certs/s000001-user_private.key
export GENAI_API_REST_CA_CERTS=/home/mleida/Descargas/s000001-user-certs/ca-cert.crt

export GENAI_GATEWAY_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/genai-gateway
export GENAI_GATEWAY_CLIENT_CERT=/path/to/user-cert.crt
export GENAI_GATEWAY_CLIENT_KEY=/path/to/user_private.key
export GENAI_GATEWAY_CA_CERTS=/path/to/ca-cert.crt

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
$ poetry run python basic_actor_chain_example/main.py
```

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
        "client_user_id": "admin",
        "client_tenant": "s000001"
      }
    }
  }
}
```
The `"config"` key with the extra metadata is normally added by GenAI API before passing the input to the chain,
but while developing locally you should add it by hand.

