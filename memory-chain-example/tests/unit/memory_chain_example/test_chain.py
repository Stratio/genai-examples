"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.
This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import pytest
from genai_core.chat_models.stratio_chat import StratioGenAIGatewayChat
from genai_core.constants.constants import CHAIN_MEMORY_KEY_CHAT_HISTORY, CHAIN_KEY_CHAT_ID
from genai_core.memory.stratio_conversation_memory import StratioConversationMemory
from genai_core.test.mock_helper import mock_init_stratio_gateway, mock_gateway_chat
from langchain_core.messages import AIMessage, HumanMessage
from pytest_mock import MockerFixture

from memory_chain_example.chain import MemoryChain


GATEWAY_ENDPOINT = "openai-chat"

# Mock values for testing
TOPIC_MOCK = "Sicily"
INPUT_MOCK_FIRST_QUESTION = "capital"
INPUT_MOCK_SECOND_QUESTION = "can you repeat?"
MOCK_CHAT_ID = "mock_chat_id"

MOCK_MODEL_RESPONSE = "The capital city of Sicily is Palermo!"
MOCK_MODEL_MEMORY_RESPONSE = "Yes, I repeat!! The capital city of Sicily is Palermo!"


@pytest.fixture
def mock_chat(mocker):
    mock_init_stratio_gateway(mocker)
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
def mock_memory(mocker: MockerFixture, mock_chat):
    return StratioConversationMemory(
        max_token_limit=1000,
        chat_model=mock_chat,
        target_uri="http://127.0.0.1:8080",
        use_ssl=False,
    )

def mock_load_save_conversation_memory(mocker) -> None:
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.save_memory",
        return_value="id",
    )
    mocker.patch(
        "genai_core.memory.stratio_conversation_memory.StratioConversationMemory.load_memory",
        return_value=[
            AIMessage(content=MOCK_MODEL_RESPONSE),
            HumanMessage(content=[{"input": INPUT_MOCK_FIRST_QUESTION, "topic": TOPIC_MOCK}]),
        ],
    )

class TestOpensearchChain:
    """
    Test suite for the OpensourceChain class.
    """

    def test_memory_chain(self, mocker, mock_chat, mock_memory):
        mocker.patch(
            "memory_chain_example.chain.MemoryChain._init_model",
            return_value=mock_chat,
        )
        mocker.patch(
            "memory_chain_example.chain.MemoryChain._init_stratio_memory",
            return_value=mock_memory,
        )

        mock_load_save_conversation_memory(mocker)
        mock_gateway_chat(mocker, MOCK_MODEL_RESPONSE)

        chain = MemoryChain(gateway_endpoint=GATEWAY_ENDPOINT).chain()
        result_first_interaction = chain.invoke(
            {"input": INPUT_MOCK_FIRST_QUESTION, "topic": TOPIC_MOCK}
        )

        assert (result_first_interaction[CHAIN_KEY_CHAT_ID])

        mock_gateway_chat(mocker, MOCK_MODEL_MEMORY_RESPONSE)

        result_second_interaction = chain.invoke({CHAIN_KEY_CHAT_ID: result_first_interaction[CHAIN_KEY_CHAT_ID], "input": INPUT_MOCK_FIRST_QUESTION, "topic": TOPIC_MOCK})

        assert(len(result_second_interaction[CHAIN_MEMORY_KEY_CHAT_HISTORY]) == 2)


if __name__ == "__main__":
    pytest.main()
