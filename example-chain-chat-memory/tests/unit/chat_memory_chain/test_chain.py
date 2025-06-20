"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.
This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

from unittest.mock import MagicMock

import pytest
from genai_core.chat_models.stratio_chat import StratioGenAIGatewayChat
from genai_core.constants.constants import (
    CHAIN_KEY_CHAT_ID,
    CHAIN_MEMORY_KEY_CHAT_HISTORY,
)
from genai_core.memory.stratio_conversation_memory import StratioConversationMemory
from genai_core.test.mock_helper import (
    mock_gateway_chat,
    mock_init_stratio_gateway_openai,
)
from langchain_core.messages import AIMessage, HumanMessage

from chat_memory_chain.chain import MemoryChain
from chat_memory_chain.constants.constants import (
    CHAIN_KEY_CONVERSATION_IS_NEW,
    CHAIN_KEY_CONVERSATION_LAST_MSG_ID,
)

GATEWAY_ENDPOINT = "openai-chat"

# Mock values for testing
DESTINATION_MOCK = "Sicily"
INPUT_MOCK_FIRST_QUESTION = "when to go?"
MOCK_MODEL_RESPONSE = (
    "The best time to visit Sicily is during the spring (April to June) and fall (September to October)."
    " \n\n- **Spring**: Mild temperatures, blooming landscapes, and fewer tourists. Ideal for outdoor activities and exploring historical sites."
    "\n- **Fall**: Warm weather, grape harvest season, and vibrant local festivals. Great for wine lovers and enjoying the beach before it gets too cool."
    "\n\nSummer (July to August) can be hot and crowded, especially in coastal areas, while winter (November to March) is cooler and quieter, "
    "but some attractions may have limited hours. \n\nChoose based on your preferences for weather and crowd levels!"
)
MOCK_CHAT_HISTORY_FIRST_QUESTION = [
    HumanMessage(
        content=INPUT_MOCK_FIRST_QUESTION, additional_kwargs={}, response_metadata={}
    ),
    AIMessage(content=MOCK_MODEL_RESPONSE, additional_kwargs={}, response_metadata={}),
]
INPUT_MOCK_SECOND_QUESTION = "I prefer another time of the year"
MOCK_MODEL_MEMORY_RESPONSE = (
    "If you prefer to visit Sicily during the winter months (November to March), here are some highlights:"
    "\n\n- **Mild Weather**: While it can be cooler, especially in January and February, "
    "temperatures are generally mild compared to many other European destinations."
    "\n- **Fewer Crowds**: Enjoy popular sites like the Valley of the Temples or Mount Etna without the usual tourist crowds."
    "\n- **Cultural Experiences**: Experience local festivals, such as the Feast of Santa Lucia in December "
    "or Carnival celebrations in February, which showcase Sicilian traditions."
    "\n- **Culinary Delights**: Winter is a great time to enjoy hearty Sicilian cuisine, "
    "including seasonal dishes and local wines.\n\nJust be prepared for some attractions to have reduced hours or be closed,"
    " especially in more remote areas. If you enjoy a quieter, more authentic experience, "
    "winter can be a lovely time to explore Sicily!"
)


@pytest.fixture
def mock_chat(mocker):
    mock_init_stratio_gateway_openai(mocker)
    mocker.patch(
        "genai_core.chat_models.stratio_chat.GatewayClient.get_endpoint_config",
        return_value={
            "id": GATEWAY_ENDPOINT,
            "endpoint_type": "llm/v2/chat",
            "model": {
                "provider": "openai",
                "name": "gpt-4o-mini-2024-07-18",
                "input_cost_1k_tokens": 0.00015,
                "output_cost_1k_tokens": 0.0006,
                "token_limit": 128000,
                "config": {
                    "stratio_credential": "openai-token",
                },
            },
        },
    )
    return StratioGenAIGatewayChat(
        endpoint=GATEWAY_ENDPOINT, target_uri="http://127.0.0.1:1080", use_ssl=False
    )


@pytest.fixture
def mock_memory(mock_chat):
    return StratioConversationMemory(
        max_token_limit=1000,
        chat_model=mock_chat,
        target_uri="http://127.0.0.1:8080",
        use_ssl=False,
    )


def mock_load_save_conversation_memory(mocker) -> None:
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.create_conversation_or_append_message",
        return_value=MagicMock(
            conversation_id="test_chat_id",
            conversation_last_msg_id="last_msg_id",
            conversation_next_msg_id="next_msg_id",
            conversation_is_new=True,
            chat_history=[],
        ),
    )
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.load_conversation",
        return_value=MagicMock(
            conversation_last_msg_id="last_msg_id",
            conversation_is_new=False,
            chat_history=[],
        ),
    )
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.update_conversation_message",
        return_value=None,
    )
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.update_conversation",
        return_value=None,
    )


def mock_load_save_conversation_memory_SECOND_QUESTION(mocker) -> None:
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.create_conversation_or_append_message",
        return_value=MagicMock(
            conversation_id="test_chat_id",
            conversation_last_msg_id="last_msg_id",
            conversation_next_msg_id="next_msg_id",
            conversation_is_new=False,
            chat_history=MOCK_CHAT_HISTORY_FIRST_QUESTION,
        ),
    )


class TestChatMemoryChain:
    """
    Test suite for the MemoryChain class.
    """

    def test_chat_memory_chain(self, mocker, mock_chat, mock_memory):
        mocker.patch(
            "chat_memory_chain.chain.MemoryChain._init_model",
            return_value=mock_chat,
        )
        mocker.patch(
            "chat_memory_chain.chain.MemoryChain._init_stratio_memory",
            return_value=mock_memory,
        )

        mock_load_save_conversation_memory(mocker)
        mock_gateway_chat(mocker, MOCK_MODEL_RESPONSE)

        chain = MemoryChain(gateway_endpoint=GATEWAY_ENDPOINT).chain()
        result_first_interaction = chain.invoke(
            {
                "input": INPUT_MOCK_FIRST_QUESTION,
                "destination": DESTINATION_MOCK,
                "config": {
                    "metadata": {
                        "__genai_state": {
                            "client_auth_type": "mtls",
                            "client_user_id": "<your-user>",
                            "client_tenant": "<your-tenant>",
                        }
                    }
                },
            }
        )

        assert result_first_interaction[CHAIN_KEY_CHAT_ID]
        assert result_first_interaction[CHAIN_KEY_CHAT_ID] == "test_chat_id"
        assert (
            result_first_interaction[CHAIN_KEY_CONVERSATION_LAST_MSG_ID]
            == "last_msg_id"
        )
        assert result_first_interaction[CHAIN_KEY_CONVERSATION_IS_NEW] is True
        assert result_first_interaction[CHAIN_MEMORY_KEY_CHAT_HISTORY] == []

        mock_load_save_conversation_memory_SECOND_QUESTION(mocker)
        mock_gateway_chat(mocker, MOCK_MODEL_MEMORY_RESPONSE)

        result_second_interaction = chain.invoke(
            {
                CHAIN_KEY_CHAT_ID: result_first_interaction[CHAIN_KEY_CHAT_ID],
                "input": INPUT_MOCK_SECOND_QUESTION,
                "destination": DESTINATION_MOCK,
            }
        )

        assert len(result_second_interaction[CHAIN_MEMORY_KEY_CHAT_HISTORY]) == 2
        assert result_second_interaction[CHAIN_KEY_CHAT_ID] == "test_chat_id"
        assert result_second_interaction[CHAIN_KEY_CONVERSATION_IS_NEW] is False


if __name__ == "__main__":
    pytest.main()
