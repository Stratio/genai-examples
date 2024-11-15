## Stratio GenAI Chain Examples

This repository is intended for developers who want to create GenAI chains using the *Stratio GenAI Core* framework so the chains can be easily be deployed in *Stratio GenAI API*.

This repository provides some simple examples of GenAI chains focused on a specific task.
There are four basic chains that you can use as a starting point to create your own chains:
 # TODO: Add the links to the chains once merged
* [Basic Actor Chain](basic-actor-chain-example/README.md): Example of a GenAI chain that implements a basic actor and invokes it.
* [Stratio Virtualizer Chain](./virtualizer-chain-example/README.md): Example of a GenAI chain that connects to the Stratio Virtualizer service to perform a query.
* [Opensearch Chain](opensearch-chain-example/README.md): Example of a GenAI chain that connects to Opensearch service and processes the result of a search.
* [Memory Chain](./README.md): Example of a GenAI chain that persist the user's conversation in order to remember the context.

Please check the readme of each chain for more information.

Stratio GenAI chains are built with [Poetry](https://python-poetry.org/docs/#installation), so in order to develop a chain you need to make sure you have the following tools in your machine:

* [Python](https://www.python.org/) >= 3.9
* [Poetry](https://python-poetry.org/docs/#installation)
* A Python editor of you choice, like [PyCharm](https://www.jetbrains.com/pycharm/) or [Visual Studio Code](https://code.visualstudio.com/)

## Local development

Stratio GenAI chains are intended to run inside *Stratio GenAI API*. In order to try out your chain while developing, *Stratio GenAI Core* provides a GenAI-API-like standalone server that can be started in your local machine to serve your chain just as if it was deployed in *Stratio GenAI API*, exposing the `invoke` endpoint and a Swagger UI. All the examples in this repository contain a `main.py` file, used to run the chain locally, where you can see how to start this standalone server. The constructor of this standalone server receives as an argument the same configuration that would be passed in the request body when registering the chain in *Stratio GenAI API*.

### Stratio GenAI Developer Proxy

Most likely, your chain will need to access some other services, such as *Stratio GenAI Gateway*, *Stratio Virtualizer*, Opensearch or *Stratio GenAI API*. Also, you need to be able to install the *Stratio GenAI Core* dependency in your Python environment. Both of these problems are solved by the *Stratio GenAI Developer Proxy*, which can be deployed in the development cluster to provide access to the services running inside the cluster, as well as to provide access to the PyPi server inside *Stratio GenAI API* containing the *Stratio GenAI Core* dependency.

Once the service in installed on your development cluster, it should be reachable through a URL like this: `https://genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080`. Then, under different paths on that server, you can access the different services. For instance, the *Stratio GenAI Gateway* would be accessed from your local machine through  `https://genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080/service/genai-gateway`. All the available services, with their path in *Stratio GenAI Developer Proxy* are listed in the following table:
| service                 | Developer proxy path                |
|-------------------------|-------------------------------------|
| *Stratio GenAI Gateway* | `/service/genai-gateway`            |
| *Stratio GenAI API*     | `/service/genai-api`                |
| *Stratio Virtualizer*   | `/service/virtualizer`              |
| Opensearch              | `/service/opensearch`               |
| *Stratio Governance*    | `/service/governance`               |
| PyPi server             | `/service/genai-api/v1/pypi/simple` |

Note that, depending on how the *Stratio GenAI Developer Proxy* is configured on the development cluster, some of these services may be not exposed.

### User authentication and authorization

When a chain that is running in *Stratio GenAI API* is invoked, several things happen:
1. *Stratio GenAI API* authenticates the invoking user.
2. *Stratio GenAI API* checks if the invoking user has a role authorized to make chain invocations.
3. *Stratio GenAI API* executes the chain, adding extra configuration metadata with information about the invoking user.
4. When the chain calls a service, it uses the identity of *Stratio GenAI API* and, if applicable, impersonates the calling user on the called service.

When running the chains locally, however, you won't have access to the *Stratio GenAI API* certificates to configure your chain to use them to authenticate itself with the services. Again, this problem is solved by the *Stratio GenAI Developer Proxy*, which does have access to the *Stratio GenAI API* credentials. It works as follows:
1. You run the chain locally configuring *your own* certificates.
2. The chain access the services through the *Stratio GenAI Developer Proxy* using *your* certificates.
3. The *Stratio GenAI Developer Proxy* checks if you are authorized to make chain invocations by checking your role on *Stratio GenAI API*.
4. When the *Stratio GenAI Developer Proxy* routes the chain requests to the corresponding service, it uses the *Stratio GenAI API* identity and, when applicable, impersonates your user.

Note that the behavior of the *Stratio GenAI Developer Proxy* in points `3` and `4` above imply that, when running the chain locally but accessing the cluster services through the *Stratio GenAI Developer Proxy*, everything works just as if the chain had been deployed in *Stratio GenAI API* and you were invoking it. Thus, if the permissions set in the cluster allow your user to invoke your chain when deployed in *Stratio GenAI API* then everything should also work correctly when running the chain locally using your own certificates. 

### User certificates and Vault client development mode

The chains may obtain the certificates needed to authenticate with other services using the Vault client provided in *Stratio GenAI Core*. To ease the development of chains from your local computer, this Vault client allows bypassing the actual access to Vault if certain environment variables are defined. When the following environment variables are defined, the Vault client will read them instead of going to Vault:
```bash
VAULT_LOCAL_CLIENT_CERT="/path/to/cert.crt"
VAULT_LOCAL_CLIENT_KEY="/path/to/private-key.key"
VAULT_LOCAL_CA_CERTS="/path/to/ca-cert.crt"
```
This way you do not need to access any Vault to develop your chain locally.

You can obtain your user certificates from *Stratio GoSec*:

1. Access to *Stratio GoSec* to manage your account. You can do it from any Stratio application like *Stratio Talk To Your Data*. In the top right corner, click on your username and select *Manage Account*.

![](./docs/manage_account_menu.png)

2. In your profile, go to the *Secrets* tab and download the *User certificate*.

![](./docs/profile_secrets.png)

3. Uncompress the ZIP file in your local machine. You will find the following files inside:

   * `ca-cert.crt`: Certificate authority
   * `<user>.crt`: User certificate
   * `<user>_private.key`: User private key

### Extra environment variables

Some clients provided in *Stratio GenAI Core*, like the *Stratio GenAI Gateway* client or the *Stratio GenAI API* client, obtain their certificates by reading some environment variables instead of accessing Vault. Some of them also expect some extra variables to be defined. In a "normal" chain execution inside *Stratio GenAI API*, these variables are alrady set in *Stratio GenAI API* container. If your chain uses these clients, you should set the corresponding environment variables to run it locally.  

For your convenience, we provide a script that generates an `.env` file with all the needed variables by just giving it the path to your certificates folder and the host of the *Stratio GenAI Developer Proxy*.

Execute the following commands to configure the environment variables:

```
$ cd genai-examples/scripts

$ python create_env_file.py      \
    --certs_path /path/to/certs  \
    --proxy_url https://genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080
```

You will find a `.env` file in the `genai-examples/scripts` folder with the environment variables.

### *Stratio GenAI Core* dependency

The dependencies of your chain are declared in the `pyproject.toml` file of your chain Poetry project, and they are managed by Poetry. The *Stratio GenAI Core* package is not public, so in order for Poetry to be able to obtain it you need to configure a Poetry source where this package can be found. The *Stratio GenAI Developer Proxy* hosts a PyPi server where the dependencies can be found.

You should edit the `pyproject.toml` file and add a block like the following (changing the url with the actual URL of your *Stratio GenAI Developer Proxy*):
```toml
[[tool.poetry.source]]
name = "genai-api-pypi"
url = "https://genai-developer-proxy-loadbalancer.s000001-genai.k8s.fifteen.labs.stratio.com:8080/service/genai-api/v1/pypi/simple/"
priority = "supplemental"
```

Also, in order to make Poetry trust this server, you need to configure it to use the CA of the cluster (the one included in the `zip` file with [your certificates](#user-certificates-and-vault-client-development-mode)):
```
$ poetry config certificates.genai-api-pypi.cert /path/to/ca-cert.crt 
```

Now you can install the dependencies in the Poetry environment:
```
$ poetry install
```

### Running your chain locally

Once you have everything configured, you can create a python script (in our examples this is the `main.py` script) where the chain is deployed inside a standalone GenAI server running in your localhost:
```python
from genai_core.server.server import GenAiServer

def main(chain_config: dict):
    "Starts a standalone server with the chain loaded"
    app = GenAiServer(
        module_name="<module-of-your-chain-class>",
        class_name="<name-of-your-chain-class>",
        # dictionary of properties that will be passed to your chain class constructor
        config=chain_config
    )
    app.start_server()

if __name__ == "__main__":
    chain_config = { 
        # here you should define the config for your chain.
        # You can do it however you want, harcoded in the script, by parsing commnad line
        # arguments or by reading environment variables (in our examples we usually read
        # environment variables)
    }
    main(chain_config)
```

#### Running from the command line

Now you can run your chain (note that the script should be called with `poetry run` to make it run in the environment of the Poetry project, which includes all the needed dependencies)
```
$ poetry run python main.py
```

This may fail if your `main.py` script or your chain expects some environment variables to be defined in order to work properly, like those pointing to your local certificates for the Vault or the Gateway client, as we explained above. If that is the case, you must set the needed environment variables before calling the script. Here we show an example setting the variables needed to [mock Vault](#user-certificates-and-vault-client-development-mode), but you can check all the variables that might be needed by generating the `.env` file with the [helper script](#extra-environment-variables).

Create a file env.sh exporting the needed variables,
```bash
export VAULT_LOCAL_CLIENT_CERT="/path/to/cert.crt"
export VAULT_LOCAL_CLIENT_KEY="/path/to/private-key.key"
export VAULT_LOCAL_CA_CERTS="/path/to/ca-cert.crt"

# add here whaterver other varialbes might be needed
# ...
# ...
```
source it
```
$ source env.sh
```
and run the script again. You will see the logs in the terminal and you can open the web interface of the chain in the browser: http://127.0.0.1:8080. 

#### Running from PyCharm

Open the Poetry project of your chain in PyCharm:

* File => Open => Select the folder

Configure the Python interpreter:

* Python Interpreter => Add New Interpreter => Add Local Interpreter => Poetry Environment => Poetry environment

Execute the chain on PyCharm. 

* Right-click on the `main.py` file => Run 'main'

This may fail if your `main.py` script or your chain expects some environment variables to be defined in order to work properly, like those pointing to your local certificates for the Vault or the Gateway client, as we explained above. If that is the case, you must set the needed environment variables before calling the script. Here we show an example setting the variables needed to [mock Vault](#user-certificates-and-vault-client-development-mode), but you can check all the variables that might be needed by generating the `.env` file with the [helper script](#extra-environment-variables), or just using that generated file.

Create a file genai.env:
```
VAULT_LOCAL_CLIENT_CERT=/path/to/cert.crt
VAULT_LOCAL_CLIENT_KEY=/path/to/private-key.key
VAULT_LOCAL_CA_CERTS=/path/to/ca-cert.crt
THIS_MAY_CONTAIN=more_variables
```
and add it to the `main.py` run configuration in PyCharm:

* Edit Configurations => Path to ".env" files => Select the `genai.env` file in the `genai-examples/scripts` folder.

![](./docs/pycharm_list_configurations.png)

![](./docs/pycharm_edit_configuration.png)

Run the `main.py` file again. You will see the logs in the PyCharm console and you can open the web interface of the chain in the browser: http://127.0.0.1:8080. 

### Useful commands

* Execute all the tests: `poetry run pytest`
* Execute only unit test: `poetry run pytest tests/unit`
* Execute only integration test: `poetry run pytest tests/integration`
* Format the code execute `poetry run black ./`
* Lint the code execute `poetry run pylint './**/'`
* Check the Python's types execute `poetry run mypy ./`

