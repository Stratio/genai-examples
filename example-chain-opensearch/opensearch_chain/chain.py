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
from genai_core.runnables.genai_auth import GenAiAuth, GenAiAuthRunnable
from genai_core.clients.vault.vault_client import VaultClient
from genai_core.logger.logger import log
from langchain_core.runnables import Runnable, chain, RunnableConfig

from opensearch_chain.constants.constants import (
    OPENSEARCH_SEARCH_VALUE_KEY,
    OPENSEARCH_COLLECTION_NAME_KEY,
    OPENSEARCH_TABLE_VALUE_KEY,
    OPENSEARCH_COLUMN_VALUE_KEY,
    OPENSEARCH_RESULT_KEY,
    OPENSEARCH_NO_RESULTS,
)
from opensearch_chain.services.opensearch_service import OpenSearchService
from opensearch_chain.constants.constants import (
    CHAIN_KEY_GENAI_AUTH,
    CHAIN_KEY_REQUEST_ID,
)


class OpenSearchChain(BaseGenAiChain, ABC):
    """
    Example of a GenAI Chain that interacts with OpenSearch service to obtain and process the result of a search.

    """

    def __init__(
        self, opensearch_url: Optional[str] = None, opensearch_min_score: int = 5
    ):
        log.info("Preparing OpenSearch Example chain")
        self.opensearch_min_score = opensearch_min_score
        self.opensearch_service = self._init_opensearch(opensearch_url)
        log.info("OpenSearch Example chain ready!")

    def _init_opensearch(self, opensearch_url: str) -> OpenSearchService:
        """
        This method initializes the OpenSearch service client to interact with an OpenSearch
         service.

        Args:
            opensearch_url (str): The URL of the OpenSearch instance.

        Returns:
            OpenSearchService: The OpenSearch service client instance.

        """
        # get certificates
        # get the needed certificates to connect to OpenSearch
        cert, key, ca = self._init_credentials()
        # Init OpenSearch
        try:
            log.info(f"Trying to connect with OpenSearch {opensearch_url}...")
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
        """
        Returns a Langchain Runnable with an invoke method. When invoking the chain,
        the body of the request will be passed to the invoke method.

        :return: A Runnable instance representing the chain.
        """

        @chain
        def _ask_opensearch(chain_data: dict) -> dict:
            """
            This method queries the OpenSearch service with the user request and returns the response.
            The response is stored in the chain_data dictionary with the key 'opensearch_response'.

            Args:
                chain_data (dict): The input data for the chain.

            Returns:
                dict: The chain data with the response from the OpenSearch service.
            """
            try:
                search_value = chain_data[OPENSEARCH_SEARCH_VALUE_KEY]
                collection_name = chain_data[OPENSEARCH_COLLECTION_NAME_KEY]
                table_value = chain_data[OPENSEARCH_TABLE_VALUE_KEY]
                column_value = chain_data[OPENSEARCH_COLUMN_VALUE_KEY]

                log.info(
                    f"Searching for value '{search_value}' in {collection_name},{table_value},{column_value}",
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
                        OPENSEARCH_NO_RESULTS,
                        chain_data,
                    )
                    chain_data[OPENSEARCH_RESULT_KEY] = OPENSEARCH_NO_RESULTS
                else:
                    first_value = search_result["hits"]["hits"][0]["_source"]["value"]
                    chain_data[OPENSEARCH_RESULT_KEY] = (
                        f"For the requested search value '{search_value}' in the column '{column_value}' of the table  '{table_value}', the first result is '{first_value}'."
                    )

            except Exception as e:
                log.error(
                    f"Unable to search index. Exception: {e}",
                    chain_data,
                )
                chain_data[OPENSEARCH_RESULT_KEY] = (
                    f"Unable to search index. Exception: {e}"
                )
            return chain_data

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

        return _extract_genai_auth | _ask_opensearch

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
