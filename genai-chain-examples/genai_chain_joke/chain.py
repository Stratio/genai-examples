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

from genai_core.chain.base import BaseGenAiChain, GenAiChainParams
from genai_core.clients.vault.vault_client import VaultClient
from genai_core.logger.logger import log
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI


class JokeChain(BaseGenAiChain, ABC):
    def __init__(
        self,
        openai_stratio_credential: str = "openai-token",
        chat_temperature: float = 0.5,
    ):
        vault_client = VaultClient()

        # openai config
        secret = vault_client.get_password(openai_stratio_credential)
        if "token" not in secret:
            raise ValueError(
                f"The secret in Vault is malformed. It has to contain the 'token' field."
            )
        self.openai_api_key = secret["token"]
        self.chat_temperature = chat_temperature

        log.info("Chain Joke ready!")

    def chain(self) -> Runnable:
        # langchain chain
        model = ChatOpenAI(
            openai_api_key=self.openai_api_key, temperature=self.chat_temperature
        )
        prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
        chain = prompt | model
        return chain

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
