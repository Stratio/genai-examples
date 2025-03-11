"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import os
from typing import Tuple, Optional

from genai_core.chain.base import BaseGenAiChain
from genai_core.logger.logger import log
from genai_core.clients.vault.vault_client import VaultClient
from genai_core.constants.constants import ENV_VAR_GENAI_API_SERVICE_NAME
from genai_core.helpers.chain_helpers import extract_uid
from genai_core.runnables.genai_auth import GenAiAuth, GenAiAuthRunnable
from langchain_core.runnables.config import RunnableConfig
from genai_core.services.virtualizer.virtualizer_service_helper import (
    VirtualizerServiceHelper,
    VirtualizerService,
)
from langchain_core.runnables import Runnable, RunnableLambda, chain

# Basic Chain specific keys
CHAIN_KEY_GENAI_AUTH = "genai_auth"
CHAIN_KEY_REQUEST_ID = "request_id"


# You should define your chains in a class inheriting from the BaseGenAiChain.
# By inheriting BaseGenAiChain you get the integration with Gen AI API, so that the chain can be
# invoked through Gen AI API once it has been deployed there. You only need to implement the
# `chain` method, which should return and "invokable" LangChain Runnable. In this example the
# chain is going to call virtualizer, so you will need also to create a virtualizer service
# that will be used in the chain itself.
class VirtualizerChain(BaseGenAiChain):
    # Example chain showing how to use GenAI Core's Virtualizer Service to run queries in Virtualizer
    # Note that, when registering the chain in GenAI API, the keys in the following sub-json of the
    # request body, "chain_config" -> "chain_params" -> {json with several keys} are the parameters
    # that will be passed here to the constructor. For local development, these parameters are
    # passed in the main.py script (which is the script start the chain for local development)

    def __init__(self, virtualizer_host: str, virtualizer_port: int):
        log.info("initiating chain")
        self.virtualizer = self._init_virtualizer(virtualizer_host, virtualizer_port)
        log.info("chain ready")

    @staticmethod
    def extract_uid(chain_data: dict) -> Optional[str]:
        """
        Given the chain data, extracts the user id.
        """
        auth = chain_data.get(CHAIN_KEY_GENAI_AUTH)
        if not isinstance(auth, GenAiAuth):
            raise AssertionError(
                f"No valid genai auth found in chain_data key '{CHAIN_KEY_GENAI_AUTH}'"
            )
        return auth.user_id_impersonated if auth.user_id_impersonated else auth.user_id

    # This should return a Langchain Runnable with an invoke method. When invoking the chain,
    # the "input" field of the request body will be passed to the invoke method of this Runnable
    def chain(self) -> Runnable:
        # In order to be able to impersonate the nominal user (the one that has invoked the chain)
        # we need to know its uid. GenAI API adds extra auth metadata to the body received in the
        # invoke request before passing it to the chain. From these metadata is possible to extract
        # the uid of the nominal user, and GenAI Core provides some Runnables to add this info
        # to the chain data. When developing locally, you should add this metadata manually to the
        # invoke request body.
        @chain
        def _extract_genai_auth(chain_data: dict, config: RunnableConfig):
            """Method to extract GenAI authentication"""
            auth = GenAiAuthRunnable().invoke(chain_data, config)
            if not isinstance(auth, GenAiAuth):
                raise AssertionError(
                    f"No valid genai auth found in chain_data key '{CHAIN_KEY_GENAI_AUTH}'"
                )
            chain_data[CHAIN_KEY_GENAI_AUTH] = auth
            #
            if auth.request_id is not None:
                chain_data[CHAIN_KEY_REQUEST_ID] = auth.request_id

            return chain_data

        return _extract_genai_auth | RunnableLambda(self._execute_query)

    def _execute_query(self, chain_data: dict) -> dict:
        # Note that you should always impersonate the nominal user so that they can only see data for which
        # they have permissions. Previous steps in the chain must have added the user info to the chain_data
        # from extra metadata that GenAI API adds to the invoke body, and we can use GenAI Core helper
        # methods to extract the userID from that extra info in the chain_data
        query = chain_data["query"]
        user = self.extract_uid(chain_data)

        # modify the query so that it is impersonated
        query = f"EXECUTE AS {user} {query}"

        # execute the query with the virtualizer service
        query_data = self.virtualizer.data_query(query)
        if query_data.successful:
            # typically each step in the chain just adds more keys to chain data
            chain_data["query_result"] = query_data.data
        else:
            # if the query fails, we can add an error message to the chain data
            chain_data["error"] = query_data.exception
        return chain_data

    def _init_virtualizer(
        self, virtualizer_host: str, virtualizer_port: int
    ) -> VirtualizerService:
        # Creates an instance of the Virtualizer service provided by GenAI Core
        # get the needed certificates to connect to virtualizer
        cert, key, ca = self._init_credentials()

        # When running inside GenAI api, this environment variable will be defined. When developing
        # locally you should set it with the name of the GenAI API service you are using in your
        # KEOS cluster, which is the user that will connect to virtualizer
        try:
            service_name = os.environ[ENV_VAR_GENAI_API_SERVICE_NAME]
        except Exception as e:
            error_msg = f"Unable to init Virtualizer Chain. The env. variable {ENV_VAR_GENAI_API_SERVICE_NAME} needs to be defined"
            log.error(error_msg)
            raise RuntimeError(error_msg) from e

        # create Virtualizer service
        try:
            # always create the virtualizer service through this helper, so we never create more than one instance
            VirtualizerServiceHelper.init_service(
                host=virtualizer_host,
                port=virtualizer_port,
                username=service_name,
                ca_certs=ca,
                client_cert=cert,
                client_key=key,
                # you could choose to make those configurable too when registering the chain
                max_attempts=3,  # graph_max_attempts,
                request_timeout=60,  # virtualizer_timeout,
            )
            # test the virtualizer connection with a simple query
            test_query = VirtualizerServiceHelper.get_service().data_query("SELECT 1")
            if test_query.exception is not None:
                raise test_query.exception
            log.info("Connected with Virtualizer Server")
        except Exception as e:
            error_msg = f"Unable to init Virtualizer Chain. Unable to validate connection to Virtualizer. Error {e}"
            log.error(error_msg)
            raise RuntimeError(error_msg) from e

        return VirtualizerServiceHelper.get_service()

    def _init_credentials(self) -> Tuple[str, str, str]:
        # This method obtains the certificates needed to access Virtualizer as a 3-tuple (cert, key, ca).
        # In production, the certificates are obtained from Vault, but for local development, you can
        # define the following environment variables and the VaultClient will use those to obtain the
        # certificates instead of trying to access Vault:
        #    VAULT_LOCAL_CLIENT_CERT
        #    VAULT_LOCAL_CLIENT_KEY
        #    VAULT_LOCAL_CA_CERTS
        # For the production case, where the chain is executed inside GenAI API, you don't need to
        # explicitly pass the Vault connection details (hot, port and token) since these fields are
        # inferred from environment variables that are automatically set by GenAI API
        try:
            vault = VaultClient()
            cert, key = vault.get_service_certificate_pem_paths()
            ca = vault.get_ca_bundle_pem_path()
            return cert, key, ca
        except Exception as e:
            error_msg = f"Unable to init Virtualizer Chain. Unable to init vault and load credentials. Error: {e}"
            log.error(error_msg)
            raise RuntimeError(error_msg) from e
