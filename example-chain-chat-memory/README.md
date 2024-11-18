# Example chain that persists the user's conversation for further interactions

This is an example of a GenAI chain that allows to remember the previous conversation in order to provide a more personalized experience.

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
# Memory chain need to access to the GenAI API in order to persist the conversation
export GENAI_API_SERVICE_NAME=genai-api-service-name.your-tenant-genai
export GENAI_API_TENANT=your-tenant
export GENAI_API_REST_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-api
export GENAI_API_REST_USE_SSL=true
export GENAI_API_REST_CLIENT_CERT=/path/to/certs/user.crt
export GENAI_API_REST_CLIENT_KEY=/path/to/certs/user_private.key
export GENAI_API_REST_CA_CERTS=/path/to/certs/ca-cert.crt

# This example needs to connect to the GenAI Gateway in order to access the LLM model through the Gateway API
export GENAI_GATEWAY_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-gateway
export GENAI_GATEWAY_USE_SSL=true
export GENAI_GATEWAY_CLIENT_CERT=/path/to/certs/user.crt
export GENAI_GATEWAY_CLIENT_KEY=/path/to/certs/user_private.key
export GENAI_GATEWAY_CA_CERTS=/path/to/certs/ca-cert.crt
```
Ensure your user have the right permissions to register memory in the GenAI API.

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment

```
$ poetry run python chat_memory_chain/main.py
```

Once started, the chain will expose a swagger UI in the following URL: `http://0.0.0.0:8080/`.

You can test your chain either via the swagger UI exposed by the local chain server, or with curl.

An example of request body for the invoke POST is the following:

Start a conversation
```json
{
  "input": {
    "destination": "Sicily",
    "input": "when to go?"
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

Continue a conversation

```json
{
  "input": {
    "destination": "Sicily",
    "input": "I prefer another time of the year",
    "chat_id": "<chat_id_returned_in_the_response>"
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