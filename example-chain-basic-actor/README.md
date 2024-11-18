# Example chain to show how to create a simple Actor and invoke it from the chain

This is an example chain to show how to define a simple actor and use it in a chain

## Local deployment

The first step in order to execute the chain in you local environment is to obtain the GenAI Developer Proxy URL and your user certificate.
After you have obtained the necessary information, please refer to the main [README.md](../README.md) for instructions on how to set up the development environment.

Finally, you can now run the chain locally by calling the `main.py` script in the poetry environment
```
$ poetry run python example_chain_basic_actor/main.py
```

In case you want to debug the chain, you can run it in PyCharm as explained in the main [README.md](../README.md) file.

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