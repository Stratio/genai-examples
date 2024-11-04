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

from genai_core.memory.chat_message_histories.wide_column import (
    WideColumnChatMessageHistory,
)
from genai_core.chain.base import BaseGenAiChain, GenAiChainParams
from genai_core.clients.vault.vault_client import VaultClient
from genai_core.logger.logger import log
from genai_core.runnables.common_runnables import (
    runnable_log,
    runnable_extract_genai_auth,
    runnable_stop_on_error,
    runnable_extract_genai_headers,
)

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


class MemoryChain(BaseGenAiChain, ABC):
    def __init__(
        self,
        openai_stratio_credential: str = "openai-token",
        chat_temperature: float = 0.5,
        memory_path: str = "memory_chain_storage",
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
        self.memory_path = memory_path

        log.info("Chain memory ready!")

    def get_session_history(self, session_id: str) -> WideColumnChatMessageHistory:
        store = WideColumnChatMessageHistory(
            f"/tmp/var/genai/{self.memory_path}", session_id
        )

        if store.conversation_id != session_id and session_id != "":
            raise RuntimeError("session_id does not exists on persisted memory.")

        if store.stats() is None:
            raise RuntimeError("memory cannot be initialized.")
        return store

    def chain(self) -> Runnable:
        # langchain chain
        model = ChatOpenAI(
            openai_api_key=self.openai_api_key, temperature=self.chat_temperature
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant about {topic}. \
                Your mission is to guide users from zero knowledge to understanding the fundamentals of {topic}. \
                Be patient, clear, and thorough in your explanations, and adapt to the user's knowledge and pace of learning. \
                Do not use synonyms to refer the {topic}",
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                ("human", "{question}"),
            ]
        )

        chain = prompt | model
        return RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="Input",
            history_messages_key="history",
        )

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
