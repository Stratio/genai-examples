"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import uuid
from abc import ABC

from genai_core.chat_models.stratio_chat import StratioGenAIGatewayChat
from genai_core.constants.constants import CHAIN_KEY_MEMORY_ID, CHAIN_KEY_CHAT_ID, CHAIN_MEMORY_KEY_CHAT_HISTORY, \
    CHAIN_KEY_INPUT_QUESTION, CHAIN_KEY_CONVERSATION_INPUT, CHAIN_KEY_CONVERSATION_OUTPUT, CHAIN_KEY_INPUT_COLLECTION
from genai_core.errors.error_code import ErrorCode
from genai_core.helpers.chain_helpers import extract_uid, update_data_with_error
from genai_core.logger.chain_logger import ChainLogger
from genai_core.memory.chat_message_histories.wide_column import (
    WideColumnChatMessageHistory,
)
from genai_core.chain.base import BaseGenAiChain, GenAiChainParams

from genai_core.logger.logger import log
from genai_core.runnables.common_runnables import runnable_extract_genai_headers, runnable_extract_genai_auth

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableLambda, ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory


class MemoryChain(BaseGenAiChain, ABC):
    def __init__(
        self,
        gateway_endpoint: str = "openai-chat",
        chat_temperature: float = 0,
        request_timeout: int = 30,
        n: int = 1,
        memory_path: str = "memory_chain_storage",
    ):
        self.gateway_endpoint = gateway_endpoint
        self.chat_temperature = chat_temperature
        self.memory_path = memory_path
        self.request_timeout = request_timeout
        self.n = n
        log.info("Memory Chain ready!")

    def create_short_memory_id(self, chain_data: dict) -> dict:
        """Creates a short memory id for actors that require chat_id to store memory"""
        chain_data[CHAIN_KEY_MEMORY_ID] = str(uuid.uuid4())
        return chain_data

    def load_and_include_chat_history(self, chain_data: dict) -> dict:
        ChainLogger.debug("Loading chat memory", chain_data)
        if CHAIN_KEY_CHAT_ID in chain_data:
            try:
                loaded_memory = self.chat_memory.load_memory(
                    user_id=extract_uid(chain_data),
                    conversation_id=chain_data[CHAIN_KEY_CHAT_ID],
                )
                if loaded_memory:
                    chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY] = loaded_memory
                    ChainLogger.info(
                        f"Successfully loaded {len(loaded_memory)} chat messages.",
                        chain_data,
                    )
            except Exception as e:
                ChainLogger.warning(
                    f"Unable to load chat history. Exception: {e}", chain_data
                )
                del chain_data[CHAIN_KEY_CHAT_ID]
                update_data_with_error(chain_data, ErrorCode.CHAT_ID_NOT_FOUND)
        return chain_data

    def save_and_include_chat_history(self, chain_data: dict) -> dict:
        """Save chat history based on the intent. Best effort"""
        try:
            ChainLogger.debug("Saving chat history...", chain_data)

            # Extract input question
            input_data = chain_data.get(CHAIN_KEY_INPUT_QUESTION)
            output_data = "No response."

            # Extract the output data based on the intent
            if self.is_sql_intent(chain_data):
                # If SQL intent, try to extract SQLActor response
                if SqlActor.actor_key in chain_data:
                    sql_actor: SqlActorOutput = chain_data.get(SqlActor.actor_key)
                    output_data = f"{sql_actor.message}\n{sql_actor.spark_sql_query}"
                elif ContextActor.actor_key in chain_data:
                    # If chain doesn't contain SQLActor, that means ContextActor stopped the execution
                    context_actor: ContextActorOutput = chain_data.get(
                        ContextActor.actor_key
                    )
                    output_data = context_actor.clarifications
            elif self.is_data_wrangler_intent(chain_data):
                # If Data Wrangler intent, try to extract DataWranglerActor response
                if DataWranglerActor.actor_key in chain_data:
                    data_wrangler_actor = chain_data.get(DataWranglerActor.actor_key)
                    output_data = f"{data_wrangler_actor.message}\n{data_wrangler_actor.spark_sql_query or ''}"
            elif self.is_schema_intent(chain_data):
                # If schema intent, extract SchemaActor response
                output_data = chain_data.get(SchemaActor.actor_key)
            elif CHAIN_KEY_INTENT in chain_data:
                # Other intents, extract the IntentActor user message
                intent_actor: IntentActorOutput = chain_data.get(IntentActor.actor_key)
                if intent_actor is not None:
                    output_data = intent_actor.user_message

            chat_id = self.chat_memory.save_memory(
                user_id=extract_uid(chain_data),
                input_msg=chain_data[CHAIN_KEY_CONVERSATION_INPUT].model_dump(
                    exclude_none=True, exclude_unset=True
                ),
                output_msg=chain_data[CHAIN_KEY_CONVERSATION_OUTPUT].model_dump(
                    exclude_none=True, exclude_unset=True
                ),
                memory_input=input_data,
                memory_output=output_data,
                title=chain_data[CHAIN_KEY_INPUT_QUESTION],
                conversation_id=chain_data.get(CHAIN_KEY_CHAT_ID),
                collection_name=chain_data.get(CHAIN_KEY_INPUT_COLLECTION),
                interaction_field=chain_data.get("interaction_field"),
                application=chain_data.get("application"),
            )
            chain_data[CHAIN_KEY_CHAT_ID] = chat_id
            ChainLogger.info(
                f"Chat history saved. Conversation Id: {chat_id}", chain_data
            )
        except Exception as e:
            ChainLogger.warning(
                f"Unable to save chat history. Exception: {e}", chain_data
            )
        return chain_data


    @property
    def chain_step_prepare_chain_and_load_memory(self) -> Runnable:
        """This step extracts headers and assigns a valid chat id to the conversation"""
        return (
            runnable_extract_genai_auth()
            | runnable_extract_genai_headers()
            | RunnableLambda(self.create_short_memory_id)
            | RunnableLambda(self.load_and_include_chat_history)
        )



    def chain(self) -> Runnable:
        # Gateway target URI is configured from environment variable
        model = StratioGenAIGatewayChat(
            endpoint=self.gateway_endpoint,
            temperature=self.chat_temperature,
            n=self.n,
            request_timeout=self.request_timeout
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant about {topic}. \
                Your mission is to guide users from zero knowledge to understanding the fundamentals of {topic}. \
                Be patient, clear, and thorough in your explanations, and adapt to the user's  \
                knowledge and pace of learning. \
                Do not use synonyms to refer the {topic}",
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                ("human", "{question}"),
            ]
        )
        chain = self.chain_step_prepare_chain_and_load_memory | RunnableLambda(self.load_and_include_chat_history) | prompt | model | self.save_and_include_chat_history
        return chain

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
