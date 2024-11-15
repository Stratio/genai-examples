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
from genai_core.constants.constants import (
    CHAIN_KEY_MEMORY_ID,
    CHAIN_KEY_CHAT_ID,
    CHAIN_MEMORY_KEY_CHAT_HISTORY,
    CHAIN_KEY_INPUT_QUESTION,
    CHAIN_KEY_CONVERSATION_INPUT,
    CHAIN_KEY_CONVERSATION_OUTPUT,
    CHAIN_KEY_INPUT_COLLECTION,
)
from genai_core.errors.error_code import ErrorCode
from genai_core.helpers.chain_helpers import extract_uid, update_data_with_error
from genai_core.logger.chain_logger import ChainLogger

from genai_core.chain.base import BaseGenAiChain, GenAiChainParams

from genai_core.logger.logger import log
from genai_core.memory.stratio_conversation_memory import StratioConversationMemory
from genai_core.model.sql_chain_models import ContentType
from genai_core.runnables.common_runnables import runnable_extract_genai_auth
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    chain,
)
from pydantic import BaseModel


class MemoryExampleMessageInput(BaseModel):
    """Class to store the input for the chat model in Conversation API."""

    input: str
    destination: str


class MemoryChain(BaseGenAiChain, ABC):
    """
    Example of a MemoryChain class that operates as a travel agent to help the user in planning a trip to a destination.
    The history of the chat is stored in a StratioConversationMemory instance.
    The chat_id is used to identify a conversation in the chat history of the StratioConversationMemory instance.
    """

    # => Conversation Cache
    chat_memory: StratioConversationMemory

    # => Model and prompt for the travel agent chat
    model = StratioGenAIGatewayChat
    prompt = ChatPromptTemplate

    def __init__(
        self,
        gateway_endpoint: str,
        chat_temperature: float = 0,
        request_timeout: int = 30,
        n: int = 1,
    ):
        """
        Initialize the MemoryChain instance.

        :param gateway_endpoint: The endpoint for the model gateway.
        The endpoint defined should correspond to the model registered in the Stratio GenAi Gateway,
        and the gateway endpoint need to be accessible through the GenAI development proxy (see README.md)
        :param chat_temperature: The temperature setting for the chat model.
        :param request_timeout: The request timeout for the chat model.
        :param n: The number of responses to generate.
        """
        log.info("Preparing Memory persistence Example chain")
        self.gateway_endpoint = gateway_endpoint
        self.chat_temperature = chat_temperature
        self.request_timeout = request_timeout
        self.n = n
        # create an instance of the StratioConversationMemory that will be used to persist the chat history
        self.chat_memory = self._init_stratio_memory()
        # create model gateway
        # Gateway target URI is configured from environment variable
        self.model = self._init_model()

        # Create a test prompt for the chat model
        # the model is an assistant that helps users prepare a trip to a user provided destination
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a travel guide about {destination}. \
                Your mission is to guide user in planning a trip to {destination}. \
                Be effective, short, clear, and try to adapt to user type of traveller, tastes and range of age.",
                ),
                MessagesPlaceholder(
                    variable_name=CHAIN_MEMORY_KEY_CHAT_HISTORY, optional=True
                ),
                ("human", "{input}"),
            ]
        )
        log.info("Memory Chain ready!")

    def _init_stratio_memory(self):
        """
        Initialize the StratioConversationMemory instance.
         create an instance of the StratioConversationMemory that will be used to persist the chat history

        :return: An instance of StratioConversationMemory.
        """

        return StratioConversationMemory(
            max_token_limit=16000,
            chat_model=StratioGenAIGatewayChat(
                endpoint=self.gateway_endpoint,
                temperature=0,
                request_timeout=self.request_timeout,
            ),
        )

    def _init_model(self):
        """
        Initialize the model gateway.
        Gateway target URI need to be configured from environment variable GENAI_GATEWAY_URL
        :return: An instance of StratioGenAIGatewayChat.
        """
        return StratioGenAIGatewayChat(
            endpoint=self.gateway_endpoint,
            temperature=self.chat_temperature,
            n=self.n,
            request_timeout=self.request_timeout,
        )

    @staticmethod
    def create_short_memory_id(chain_data: dict) -> dict:
        """
        Creates a short memory id for chains that require chat_id to store memory.

        :param chain_data: The chain data dictionary.
        :return: The updated chain data dictionary with a new memory id.
        """
        chain_data[CHAIN_KEY_MEMORY_ID] = str(uuid.uuid4())
        return chain_data

    def load_and_include_chat_history(self, chain_data: dict) -> dict:
        """
        Load and include chat history in the chain data.
        This data will be returned to the user as part of the response.
        The conversation is identified by the chat_id.
        If the request does not contain a chat_id, the chat history will not be loaded,
         and it will be treated as a new conversation.

        :param chain_data: The chain data dictionary.
        :return: The updated chain data dictionary with chat history included.
        """
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
        """
        Save chat in the history of the conversation.
        The conversation is identified by the chat_id.

        :param chain_data: The chain data dictionary.
        :return: The updated chain data dictionary with chat history saved.
        """
        try:
            ChainLogger.debug("Saving chat history...", chain_data)

            # Extract input question
            input_data = chain_data.get(CHAIN_KEY_INPUT_QUESTION)
            output_data = "No response."

            # Extract the output data based on the intent
            if CHAIN_KEY_CONVERSATION_OUTPUT in chain_data:
                output_data = chain_data[CHAIN_KEY_CONVERSATION_OUTPUT]["content"]

            chat_id = self.chat_memory.save_memory(
                user_id=extract_uid(chain_data),
                input_msg=chain_data[CHAIN_KEY_CONVERSATION_INPUT].model_dump(
                    exclude_none=True, exclude_unset=True
                ),
                output_msg=chain_data[CHAIN_KEY_CONVERSATION_OUTPUT],
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

    def chain(self) -> Runnable:
        """
        Define the chain for a conversation with the travel agent.

        :return: A Runnable instance representing the chain.
        """
        @chain
        def _plan_trip_to_destination(chain_data: dict) -> dict:
            """
            Ask a question to the travel agent.

            :param chain_data: The chain data dictionary.
            :return: The updated chain data dictionary with the model's response.
            """
            chain_data[
                CHAIN_KEY_CONVERSATION_INPUT
            ] = MemoryExampleMessageInput.model_validate(chain_data)
            topic_chain = self.prompt | self.model
            chain_output = {}
            chain_output.update(
                {
                    "content_type": ContentType.MESSAGE,
                    "content": topic_chain.invoke(chain_data).content,
                }
            )
            chain_data[CHAIN_KEY_CONVERSATION_OUTPUT] = chain_output
            return chain_data

        memory_chain = (
            # the runnable_extract_genai_auth is used to extract the auth information from the metadata which is used by the load_memory method
            runnable_extract_genai_auth()
            | RunnableLambda(self.create_short_memory_id)
            | RunnableLambda(self.load_and_include_chat_history)
            | _plan_trip_to_destination
            | self.save_and_include_chat_history
        )
        return memory_chain

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
