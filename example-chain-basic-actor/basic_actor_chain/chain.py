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

from langchain_core.runnables import Runnable, chain
from genai_core.chain.base import BaseGenAiChain
from genai_core.runnables.genai_auth import GenAiAuthRunnable
from genai_core.logger.logger import log
from genai_core.runnables.genai_auth import GenAiAuth
from .actors.basic_actor import BasicExampleActor
from .constants.constants import CHAIN_KEY_USER_NAME, CHAIN_KEY_GENAI_AUTH
from langchain_core.runnables import RunnableConfig


# Here you define your chain, which inherits from the BaseGenAiChain, so you only need to implement
# the `chain` method. Note that this chain is using a custom basic actor that needs to be instantiated with the gateway endpoint (the LLM model used).
# the model need to be registered in the Stratio Gateway, and the gateway_endpoint variable is the id of the model in the gateway.
class BasicActorChain(BaseGenAiChain, ABC):
    # Actor instance of BasicExampleActor, which will be used in the chain
    basic_actor: BasicExampleActor

    def __init__(self, gateway_endpoint: str, llm_timeout: int = 30):
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
        """
        Returns a Langchain Runnable with an invoke method. When invoking the chain,
        the body of the request will be passed to the invoke method.

        :return: A Runnable instance representing the chain.
        """

        @chain
        def _invoke_actor(chain_data: dict):
            """
            Invokes the actor with the given chain data.

            :param chain_data: The data passed through the chain.
            :return: The result of the actor's invocation.
            """
            return self.basic_actor.get_chain().invoke(chain_data)

        @chain
        def _extract_user_name(chain_data: dict):
            """
            Extracts the username from the chain data.

            :param chain_data: The data passed through the chain.
            :return: The username extracted from the chain data.
            """
            # The actor replies differently in case the username is Alice.
            # This step extracts the username from the auth metadata extracted by the _extract_genai_auth runnable.
            auth = chain_data.get(CHAIN_KEY_GENAI_AUTH)
            if not isinstance(auth, GenAiAuth):
                raise AssertionError(
                    f"No valid genai auth found in chain_data key '{CHAIN_KEY_GENAI_AUTH}'"
                )
            chain_data[CHAIN_KEY_USER_NAME] =  auth.user_id_impersonated if auth.user_id_impersonated else auth.user_id

            return chain_data

        @chain
        def _extract_genai_auth(
                chain_data: dict, config: RunnableConfig
        ):
            """
            Method to extract GenAI authentication from the chain data and config.

            :param chain_data: The data passed through the chain.
            :param config: The configuration for the runnable.
            :return: The chain data with the GenAI authentication added.
            """

            auth = GenAiAuthRunnable().invoke(chain_data, config)
            if not isinstance(auth, GenAiAuth):
                raise AssertionError(
                    f"No valid genai auth found in chain_data key '{CHAIN_KEY_GENAI_AUTH}'"
                )
            chain_data[CHAIN_KEY_GENAI_AUTH] = auth
            return chain_data

        # The chain is composed of three runnables steps:
        # _extract_genai_auth, _extract_user_name and _invoke_actor.
        # GenAI API adds extra auth metadata to the body received in the
        # invoke request before passing it to the chain. From these metadata is
        # possible to extract the uid of the nominal user.
        # When developing locally, you should add this metadata manually
        # to the invoke request body as part of the config section of the body (see README.md).
        # for ths reason the first step is to extract the auth metadata.

        return _extract_genai_auth | _extract_user_name | _invoke_actor
