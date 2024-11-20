# Example chain to show how to create a simple Actor and invoke it from the chain

This is an example showing how to define a simple actor and use it in a basic question-answering chain.

## Local deployment

We assume that you already have poetry installed. If not, you can install it from [here](https://python-poetry.org/docs/#installation).

Verify that you have a dependencies source in your `pyproject.toml` with the URL of a PyPi server providing the *Stratio GenAI Core* dependency, like the one in *Stratio GenAI Developer Proxy*.
Note that the URL below is just an example and you should add the correct URL for your case.

```toml
[[tool.poetry.source]]
name = "stratio-releases"
url = "https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-api/v1/pypi/simple/"
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

Set up the needed environment variables. You can create a file `env.sh` like the following (or use the [helper script](../README.md#extra-environment-variables)):

```bash
# These variables are used by the GenAI Gateway client to access the Gateway
export GENAI_GATEWAY_URL=https://genai-developer-proxy-loadbalancer.your-tenant-genai.yourdomain.com:8080/service/genai-gateway
export GENAI_GATEWAY_USE_SSL=true
export GENAI_GATEWAY_CLIENT_CERT=/path/to/certs/user.crt
export GENAI_GATEWAY_CLIENT_KEY=/path/to/certs/user_private.key
export GENAI_GATEWAY_CA_CERTS=/path/to/certs/ca-cert.crt
```
and then source it (or [add to PyCharm](../README.md#running-from-pycharm))
```
$ source env.sh
```

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment (or [run from PyCharm](../README.md#running-from-pycharm)):
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
  }
}
```

The `"config"` key with the extra metadata about the user that has invoked the chain is normally added by GenAI API before passing the input to the chain, but while developing locally you should add it by hand.
