"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

import uuid
from abc import ABC
from typing import Optional

from genai_core.clients.api.api_client_model import ConversationState
from genai_core.chat_models.stratio_chat import StratioGenAIGatewayChat
from genai_core.constants.constants import (
    CHAIN_KEY_MEMORY_ID,
    CHAIN_KEY_CHAT_ID,
    CHAIN_MEMORY_KEY_CHAT_HISTORY,
    CHAIN_KEY_INPUT_QUESTION,
    CHAIN_KEY_CONVERSATION_INPUT,
    CHAIN_KEY_CONVERSATION_OUTPUT,
    CHAIN_KEY_INPUT_COLLECTION,
    CHAIN_KEY_CONTENT,
)
from genai_core.errors.error_code import ErrorCode
from genai_core.graph.graph_data import GraphData
from genai_core.logger.chain_logger import ChainLogger
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from genai_core.memory.stratio_conversation_memory import CreateConversation
from genai_core.model.sql_chain_models import SqlChatMessageInput


from genai_core.chain.base import BaseGenAiChain, GenAiChainParams

from chat_memory_chain.constants.constants import *
from genai_core.logger.logger import log
from genai_core.memory.stratio_conversation_memory import StratioConversationMemory
from genai_core.model.sql_chain_models import ContentType, SqlChatMessageOutput
from langchain_core.runnables import RunnableConfig
from genai_core.runnables.genai_auth import GenAiAuthRunnable
from genai_core.runnables.genai_auth import GenAiAuth
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

    data = GraphData

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
        # create model, Gateway target URI is configured from environment variable
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
    def create_short_memory_id_and_conversation_output(chain_data: dict) -> dict:
        """
        Creates a short memory id for chains that require chat_id to store memory.

        :param chain_data: The chain data dictionary.
        :return: The updated chain data dictionary with a new memory id.
        """
        chain_data[CHAIN_KEY_MEMORY_ID] = str(uuid.uuid4())
        chain_data[CHAIN_KEY_CONVERSATION_INPUT] = SqlChatMessageInput(**chain_data)

        return chain_data

    @staticmethod
    def extract_uid(chain_data: dict) -> Optional[str]:
        """
        Given the chain data, extracts the user id.

        param chain_data: The chain data dictionary.
        return: The user id.
        """
        auth = chain_data.get(CHAIN_KEY_GENAI_AUTH)
        if not isinstance(auth, GenAiAuth):
            raise AssertionError(
                f"Genai auth not found or invalid auth data in chain_data key '{CHAIN_KEY_GENAI_AUTH}'"
            )
        return auth.user_id_impersonated if auth.user_id_impersonated else auth.user_id

    def base_chain_output(self, chain_data: dict) -> dict:
        """
        Returns the base output for a chain

        :param chain_data: The chain data dictionary.
        :return: The base output for a chain.
        """
        return {
            "intent": chain_data.get(CHAIN_KEY_INTENT) or "other",
            "version": 2,
        }

    def running_chain_output(self, chain_data: dict) -> SqlChatMessageOutput:
        """
        Returns the output for a running chain

        :param chain_data: The chain data dictionary.
        :return: The output for a running chain.
        """
        output = self.base_chain_output(chain_data) | {
            "content_type": ContentType.MESSAGE,
            "content": {"message": "..."},
        }
        return SqlChatMessageOutput.model_validate(output)

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

        ChainLogger.debug(
            "Loading chat memory", graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA)
        )

        chain_data[CHAIN_KEY_REASONING] = []
        if chain_data.get(CHAIN_KEY_SAVE_CONVERSATION) is None:
            chain_data[CHAIN_KEY_SAVE_CONVERSATION] = True
        ChainLogger.debug(
            f"Loading chat history. Conversation Id: {chain_data.get(CHAIN_KEY_CHAT_ID)} Message Id: {chain_data.get(CHAIN_KEY_CHAT_MESSAGE_ID)} "
            f"Save Conversation: {chain_data.get(CHAIN_KEY_SAVE_CONVERSATION)}",
            graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
        )

        try:
            if chain_data[CHAIN_KEY_SAVE_CONVERSATION]:
                self._load_or_create_conversation(chain_data)
            else:
                self._load_conversation(chain_data)
        except Exception as e:
            ChainLogger.warning(
                f"Unable to load chat history. Conversation Id {chain_data.get(CHAIN_KEY_CHAT_ID)} "
                f"Message Id: {chain_data.get(CHAIN_KEY_CHAT_MESSAGE_ID)}. Exception: {e}",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )
            chain_data[CHAIN_KEY_CHAT_ID] = None
            (
                chain_data["halt_execution"](ErrorCode.CONVERSATION_ERROR)
                if "halt_execution" in chain_data
                else None
            )

        if chain_data.get(CHAIN_MEMORY_KEY_CHAT_HISTORY):
            chat_history_str = []
            for msg in chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY]:
                if isinstance(msg, HumanMessage):
                    chat_history_str.append(f"\t<human>{msg.content}</human>")
                elif isinstance(msg, AIMessage):
                    chat_history_str.append(f"\t<ai>{msg.content}</ai>")
                elif isinstance(msg, SystemMessage):
                    chat_history_str.append(f"\t<system>{msg.content}</system>")
            chat_history_str = "\n".join(chat_history_str)
            chain_data[CHAIN_KEY_CHAT_HISTORY_STR] = chat_history_str

        return chain_data

    def save_and_include_chat_history(self, chain_data: dict) -> dict:
        """
        Save chat in the history of the conversation.
        The conversation is identified by the chat_id.

        :param chain_data: The chain data dictionary.
        :return: The updated chain data dictionary with chat history saved.
        """
        if (
            not chain_data.get(CHAIN_KEY_SAVE_CONVERSATION)
            or chain_data.get(CHAIN_KEY_CONVERSATION_LAST_MSG_ID) is None
        ):
            # if the conversation was not created, we should not save it.
            # this happens when the parameter save_conversation is false or when the chain input is invalid
            ChainLogger.info(
                "Skipping saving chat history.",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )
            return chain_data

        try:
            ChainLogger.debug(
                f"Saving chat history... Conversation Id {chain_data.get(CHAIN_KEY_CHAT_ID)}",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )

            chain_data[CHAIN_KEY_MEMORY_OUTPUT] = self._extract_memory_output(
                chain_data
            )

            user_id = self.extract_uid(chain_data)
            self.chat_memory.update_conversation_message(
                user_id=user_id,
                conversation_id=chain_data.get(CHAIN_KEY_CHAT_ID),
                conversation_msg_id=chain_data.get(CHAIN_KEY_CONVERSATION_LAST_MSG_ID),
                memory_input=chain_data.get(CHAIN_KEY_INPUT_QUESTION),
                memory_output=chain_data.get(CHAIN_KEY_MEMORY_OUTPUT),
                input_msg=chain_data.get(CHAIN_KEY_CONVERSATION_INPUT).model_dump(
                    exclude_none=True, exclude_unset=True
                ),
                output_msg=chain_data.get(CHAIN_KEY_CONVERSATION_OUTPUT),
                reasoning=chain_data.get(CHAIN_KEY_REASONING),
                chat_history=chain_data.get(CHAIN_MEMORY_KEY_CHAT_HISTORY),
                suggested_msg=chain_data.get(CHAIN_KEY_SUGGESTED_MSG),
            )

            title = None
            if (
                chain_data.get(CHAIN_KEY_CONVERSATION_IS_NEW)
                and chain_data.get(CHAIN_KEY_CONVERSATION_ACTOR) is not None
            ):
                title = chain_data[CHAIN_KEY_CONVERSATION_ACTOR].title
            self.chat_memory.update_conversation(
                user_id=user_id,
                conversation_id=chain_data.get(CHAIN_KEY_CHAT_ID),
                title=title,
                state=ConversationState.FINISHED.value,
            )
            ChainLogger.info(
                f"Chat history saved. Conversation Id: {chain_data.get(CHAIN_KEY_CHAT_ID)} "
                f"(Message Id: {chain_data.get(CHAIN_KEY_CONVERSATION_LAST_MSG_ID)})",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )
        except Exception as e:
            ChainLogger.warning(
                f"Unable to save chat history. Conversation Id: {chain_data.get(CHAIN_KEY_CHAT_ID)}. Exception: {e}",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )
            (
                chain_data["halt_execution"](ErrorCode.CONVERSATION_ERROR)
                if "halt_execution" in chain_data
                else None
            )

        return chain_data

    def _extract_memory_output(self, chain_data: dict) -> str:
        """
        Define what is the memory output to be saved

        :param chain_data: The chain data dictionary.
        :return: The memory output to be saved.
        """

        if (chain_data.get(CHAIN_KEY_CONVERSATION_OUTPUT)).get(CHAIN_KEY_CONTENT):
            return f"{chain_data[CHAIN_KEY_CONVERSATION_OUTPUT][CHAIN_KEY_CONTENT]}"

        return "No response."

    def _load_or_create_conversation(self, chain_data: dict):
        """
        Load or create a new conversation.

        :param chain_data: The chain data dictionary.
        :return: Create a new conversation or load all the chat messages from the conversation.
        """
        output = self.running_chain_output(chain_data)
        create_conversation = CreateConversation(
            input_msg=chain_data[CHAIN_KEY_CONVERSATION_INPUT].model_dump(
                exclude_none=True, exclude_unset=True
            ),
            output_msg=output.model_dump(exclude_none=True, exclude_unset=True),
            reasoning=chain_data[CHAIN_KEY_REASONING],
            title=chain_data[CHAIN_KEY_INPUT_QUESTION],
            state=ConversationState.RUNNING.value,
            collection_name=(
                chain_data[CHAIN_KEY_INPUT_COLLECTION]
                if CHAIN_KEY_INPUT_COLLECTION in chain_data
                else None
            ),
            interaction_field=(
                chain_data[CHAIN_KEY_INTERACTION_FIELD]
                if CHAIN_KEY_INTERACTION_FIELD in chain_data
                else None
            ),
            application=(
                chain_data[CHAIN_KEY_APPLICATION]
                if CHAIN_KEY_APPLICATION in chain_data
                else None
            ),
            suggested_msg=list(),
        )

        conversation_memory = self.chat_memory.create_conversation_or_append_message(
            user_id=self.extract_uid(chain_data),
            conversation_id=(
                chain_data.get(CHAIN_KEY_CHAT_ID)
                if CHAIN_KEY_CHAT_ID in chain_data
                else None
            ),
            conversation_msg_id=(
                chain_data.get(CHAIN_KEY_CHAT_MESSAGE_ID)
                if CHAIN_KEY_CHAT_MESSAGE_ID in chain_data
                else None
            ),
            create_conversation=create_conversation,
        )
        chain_data[CHAIN_KEY_CHAT_ID] = conversation_memory.conversation_id
        chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID] = (
            conversation_memory.conversation_last_msg_id
        )
        chain_data[CHAIN_KEY_CONVERSATION_IS_NEW] = (
            conversation_memory.conversation_is_new
        )
        chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY] = conversation_memory.chat_history
        if conversation_memory.conversation_is_new:
            ChainLogger.info(
                f"Successfully created new conversation '{chain_data[CHAIN_KEY_CHAT_ID]}' "
                f"(Message Id: {chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID]}).",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )
        else:
            ChainLogger.info(
                f"Successfully loaded {len(chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY])} chat messages from "
                f"conversation '{chain_data[CHAIN_KEY_CHAT_ID]}' (Message Id: {chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID]}).",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )

    def _load_conversation(self, chain_data: dict):
        """
        Load a conversation from the memory.

        :param chain_data: The chain data dictionary.
        :return: Load all the chat messages from the conversation.
        """
        conversation_memory = None
        if chain_data.get(CHAIN_KEY_CHAT_ID) is not None:
            conversation_memory = self.sql_chain.chat_memory.load_conversation(
                user_id=self.extract_uid(chain_data),
                conversation_id=chain_data.get(CHAIN_KEY_CHAT_ID),
                conversation_msg_id=chain_data.get(CHAIN_KEY_CHAT_MESSAGE_ID),
            )

        if conversation_memory is None:
            chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID] = None
            chain_data[CHAIN_KEY_CONVERSATION_IS_NEW] = True
            chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY] = []
            ChainLogger.info(
                f"Conversation '{chain_data[CHAIN_KEY_CHAT_ID]}' (Message Id: {chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID]}) not found. "
                "A new conversation won't be created because 'save_conversation' parameter is set to False.",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )
        else:
            chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID] = (
                conversation_memory.conversation_last_msg_id
            )
            chain_data[CHAIN_KEY_CONVERSATION_IS_NEW] = (
                conversation_memory.conversation_is_new
            )
            chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY] = conversation_memory.chat_history
            ChainLogger.info(
                f"Successfully loaded {len(chain_data[CHAIN_MEMORY_KEY_CHAT_HISTORY])} chat messages from "
                f"conversation '{chain_data[CHAIN_KEY_CHAT_ID]}' (Message Id: {chain_data[CHAIN_KEY_CONVERSATION_LAST_MSG_ID]}).",
                graph_data=chain_data.get(CHAIN_KEY_GRAPH_DATA),
            )

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
            chain_data[CHAIN_KEY_CONVERSATION_INPUT] = (
                MemoryExampleMessageInput.model_validate(chain_data)
            )
            travel_agent_chain = self.prompt | self.model
            chain_output = {
                "content_type": ContentType.MESSAGE,
                "content": travel_agent_chain.invoke(chain_data).content,
            }
            chain_data[CHAIN_KEY_CONVERSATION_OUTPUT] = chain_output
            return chain_data

        @chain
        def _extract_genai_auth(chain_data: dict, config: RunnableConfig):
            """
            Method to extract GenAI authentication from the chain data and config.

            :param chain_data: The data passed through the chain.
            :param config: The configuration for the runnable.
            :return: The chain data with the GenAI authentication added.
            """

            auth = GenAiAuthRunnable().invoke(chain_data, config)
            if not isinstance(auth, GenAiAuth):
                raise AssertionError(
                    f"Genai auth not found or invalid auth data in chain_data key '{CHAIN_KEY_GENAI_AUTH}'"
                )
            chain_data[CHAIN_KEY_GENAI_AUTH] = auth
            #
            if auth.request_id is not None:
                chain_data[CHAIN_KEY_REQUEST_ID] = auth.request_id

            chain_data[CHAIN_KEY_GRAPH_DATA] = GraphData(**chain_data)

            return chain_data

        chat_memory_chain = (
            # the runnable_extract_genai_auth is used to extract the auth
            # information from the metadata which is used by the load_memory method
            _extract_genai_auth
            | RunnableLambda(self.create_short_memory_id_and_conversation_output)
            | RunnableLambda(self.load_and_include_chat_history)
            | _plan_trip_to_destination
            | self.save_and_include_chat_history
        )
        return chat_memory_chain

    def chain_params(self) -> GenAiChainParams:
        """
        Define the chain parameters.

        :return: The chain parameters.
        """

        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
