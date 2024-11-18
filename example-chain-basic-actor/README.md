# Example chain to show how to create a simple Actor and invoke it from the chain

This is an example showing how to define a simple actor and use it in a basic question-answering chain.

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
export GENAI_GATEWAY_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-gateway
export GENAI_GATEWAY_USE_SSL=true
export GENAI_GATEWAY_CLIENT_CERT=/path/to/certs/user.crt
export GENAI_GATEWAY_CLIENT_KEY=/path/to/certs/user_private.key
export GENAI_GATEWAY_CA_CERTS=/path/to/certs/ca-cert.crt
```
and then source it (or add to PyCharm)
```
$ source env.sh
```

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment:
```
$ poetry run python basic_actor_chain/main.py
```

Once started, the chain will expose a swagger UI in the following URL: `http://0.0.0.0:8080/`.

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