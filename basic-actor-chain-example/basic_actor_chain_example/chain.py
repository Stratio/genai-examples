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
from typing import Optional, cast

from genai_core.chain.base import BaseGenAiChain
from genai_core.constants.constants import CHAIN_KEY_GENAI_HEADERS, CHAT_LANGUAGE_ENGLISH, CHAT_LANGUAGE_SPANISH, \
    CHAIN_KEY_LANGUAGE
from genai_core.helpers.chain_helpers import extract_uid
from genai_core.logger.logger import log
from genai_core.runnables.genai_headers import GenAiHeaders, Language
from langchain_core.runnables import Runnable, RunnableLambda
from genai_core.runnables.common_runnables import runnable_extract_genai_auth
from .actors.basic_actor import BasicExampleActor
from .constants.constants import CHAIN_KEY_USER_NAME

# Here you define your chain, which inherits from the BaseGenAiChain, so you only need to implement
# the `chain` method. Note that this chain is using a custom basic actor that needs to be instantiated with the gateway endpoint (the LLM model used).
# the model need to be registered in the Stratio Gateway, and the gateway_endpoint variable is the id of the model in the gateway.
class BasicActorChain(BaseGenAiChain, ABC):
    # Actor instance of BasicExampleActor, which will be used in the chain
    basic_actor: BasicExampleActor

    # Internal chain
    _chain: Optional[Runnable] = None
    def __init__(
        self,
        gateway_endpoint: str,
        llm_timeout: int = 30
    ):
        """
        Initializes the BasicActorChain with the given gateway endpoint and timeout.

        :param gateway_endpoint: The ID of the endpoint in the GenAI Gateway pointing to the desired .
        :param llm_timeout: Timeout for the LLM model, default is 30 seconds.
        """
        log.info("Preparing Basic Actor Example chain")
        self.basic_actor = BasicExampleActor(
            gateway_endpoint=gateway_endpoint,
            timeout=llm_timeout,
        )
        log.info("Basic Actor Example chain ready!")

    # This should return a Langchain Runnable with an invoke method. When invoking the chain,
    # the body of the request will be passed to the invoke method
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
        return (runnable_extract_genai_auth()
                | RunnableLambda(self._extract_language)
                | RunnableLambda(self._extract_username)
                | RunnableLambda(self._invoke_actor))

    @staticmethod
    def _extract_language(chain_data: dict) -> dict:
        """
        Extracts desired output language from headers or sets English by default.

        :param chain_data: The data passed through the chain.
        :return: Updated chain data with the extracted language.
        """
        headers = cast(GenAiHeaders, chain_data.get(CHAIN_KEY_GENAI_HEADERS))
        language = headers.language if headers else None
        # Set default language as English
        language_str = CHAT_LANGUAGE_ENGLISH
        if language is not None:
            log.info(f"Requested language: {language.value}", chain_data)
            if language == Language.SPANISH.value:
                language_str = CHAT_LANGUAGE_SPANISH
        else:
            log.warning(
                "Language is not found in headers. Setting language to english.",
                chain_data,
            )

        # Extract language from headers
        chain_data[CHAIN_KEY_LANGUAGE] = language_str
        return chain_data

    @staticmethod
    def _extract_username(chain_data: dict):
        # Note that you should always impersonate the nominal user so that they can only see data for which
        # they have permissions. Previous steps in the chain must have added the user info to the chain_data
        # from extra metadata that GenAI API adds to the invoke body, and we can use GenAI Core helper
        # methods to extract the userID from that extra info in the chain_data
        """
        Extracts the user ID from the chain data and adds it to the chain data.

        :param chain_data: The data passed through the chain.
        :return: Updated chain data with the extracted user ID.
        """
        chain_data[CHAIN_KEY_USER_NAME] = extract_uid(chain_data)

        return chain_data

    def _invoke_actor(self, chain_data: dict):
        # Note that you should always impersonate the nominal user so that they can only see data for which
        # they have permissions. Previous steps in the chain must have added the user info to the chain_data
        # from extra metadata that GenAI API adds to the invoke body, and we can use GenAI Core helper
        # methods to extract the userID from that extra info in the chain_data
        """
        Invokes the actor with the given chain data.

        :param chain_data: The data passed through the chain.
        :return: The result of the actor's invocation.
        """
        return self.basic_actor.get_chain().invoke(chain_data)

