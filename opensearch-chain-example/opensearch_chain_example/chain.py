"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from abc import ABC
from typing import Optional

from genai_core.chain.base import BaseGenAiChain
from genai_core.clients.vault.vault_client import VaultClient
from genai_core.logger.logger import log
from genai_core.runnables.common_runnables import runnable_extract_genai_auth
from langchain_core.runnables import Runnable, chain

from opensearch_chain_example.constants.constants import (
    OPENSEARCH_SEARCH_VALUE_KEY,
    OPENSEARCH_COLLECTION_NAME_KEY,
    OPENSEARCH_TABLE_VALUE_KEY,
    OPENSEARCH_COLUMN_VALUE_KEY,
    OPENSEARCH_EXPLANATION_KEY,
)
from opensearch_chain_example.services.opensearch_service import OpenSearchService


# Here you define your chain, which inherits from the BaseGenAiChain, so you only need to implement
# the `chain` method. Note that this chain is using a custom basic actor that needs to be instantiated with the gateway endpoint (the LLM model used).
# the model need to be registered in the Stratio Gateway, and the gateway_endpoint variable is the id of the model in the gateway.
class OpensourceChain(BaseGenAiChain, ABC):
    # Internal chain
    _chain: Optional[Runnable] = None

    def __init__(
        self, opensearch_url: Optional[str] = None, opensearch_min_score: int = 5
    ):
        log.info("Preparing OpenSearch Example chain")
        self.opensearch_min_score = opensearch_min_score
        self.opensearch_service = self._init_opensearch(opensearch_url)
        log.info("OpenSearch Example chain ready!")

    def _init_opensearch(self, opensearch_url: str) -> OpenSearchService:
        # get certificates
        # get the needed certificates to connect to OpenSearch
        cert, key, ca = self._init_credentials()
        # Init OpenSearch
        try:
            log.info(
                f"Trying to connect with OpenSearch {opensearch_url}..."
            )
            opensearch_service = OpenSearchService(
                opensearch_url=opensearch_url,
                ca_certs=ca,
                client_cert=cert,
                client_key=key,
            )
            assert opensearch_service.client.indices.get_alias("*")
            log.info(f"Connected with OpenSearch")
        except Exception as error:
            error_msg = f"Unable to init OpenSearch Chain. Unable to validate connection with OpenSearch. Error: {error}"
            log.error(error_msg)
            raise RuntimeError(error_msg)
        return opensearch_service

    def chain(self) -> Runnable:
        # In order to be able to impersonate the nominal user (the one that has invoked the chain)
        # we need to know its uid. GenAI API adds extra auth metadata to the body received in the
        # invoke request before passing it to the chain. From these metadata is possible to extract
        # the uid of the nominal user, and GenAI Core provides some Runnables to add this info
        # to the chain data. When developing locally, you should add this metadata manually to the
        # invoke request body.
        """
        Returns a Langchain Runnable with an invoke method. When invoking the chain,
        the body of the request will be passed to the invoke method.

        :return: A Runnable instance representing the chain.
        """

        @chain
        def _ask_opensearch(chain_data: dict) -> dict:
            """
            This method queries the OpenSearch service with the user request and returns the response.
            """
            try:
                search_value = chain_data[OPENSEARCH_SEARCH_VALUE_KEY]
                collection_name = chain_data[OPENSEARCH_COLLECTION_NAME_KEY]
                table_value = chain_data[OPENSEARCH_TABLE_VALUE_KEY]
                column_value = chain_data[OPENSEARCH_COLUMN_VALUE_KEY]

                log.info(
                    f"Searching parametric filter value '{search_value}' for {collection_name},{table_value},{column_value}",
                    chain_data,
                )
                search_result = self.opensearch_service.search_filter_values(
                    collection_name,
                    table_value,
                    column_value,
                    search_value,
                    self.opensearch_min_score,
                )
                if len(search_result["hits"]["hits"]) == 0:
                    log.info(
                        f"No parametric filter found.",
                        chain_data,
                    )
                    chain_data[
                        OPENSEARCH_EXPLANATION_KEY
                    ] = f"No parametric filter found."
                else:
                    first_value = search_result["hits"]["hits"][0]["_source"]["value"]
                    chain_data[
                        OPENSEARCH_EXPLANATION_KEY
                    ] = f"To obtain the requested value '{search_value}' in the column '{column_value}' of the table  '{table_value}', the exact value to filter is '{first_value}'."

            except Exception as e:
                log.error(
                    f"Unable to extract filter instructions. Exception: {e}",
                    chain_data,
                )
                chain_data[
                    OPENSEARCH_EXPLANATION_KEY
                ] = f"Unable to extract filter instructions. Exception: {e}"
            return chain_data

        return runnable_extract_genai_auth() | _ask_opensearch

    @staticmethod
    def _init_credentials():
        """
        This method obtains and sets the certificates needed to access OpenSearch service.
        In production, the certificates are obtained from Vault, but for local development, you can
        define the following environment variables and the VaultClient will use those to obtain the
        certificates instead of trying to access Vault:
           VAULT_LOCAL_CLIENT_CERT
           VAULT_LOCAL_CLIENT_KEY
           VAULT_LOCAL_CA_CERTS
        For the production case, where the chain is executed inside GenAI API, you don't need to
        explicitly pass the Vault connection details (hot, port and token) since these fields are
        inferred from environment variables that are automatically set by GenAI API
        """
        try:
            vault = VaultClient()
            cert, key = vault.get_service_certificate_pem_paths()
            ca = vault.get_ca_bundle_pem_path()
            return cert, key, ca
        except Exception as e:
            error_msg = f"Unable to init OpenSearch Chain. Unable to init vault and load credentials. Error: {e}"
            log.error(error_msg)
            raise RuntimeError(error_msg) from e
