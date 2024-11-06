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

from pytest_mock import MockerFixture

from genai_chain_gateway.chain import GatewayChain


def mock_gateway(mocker: MockerFixture, msg_output: str, n: int) -> None:
    class MockGatewayClient:
        def __init__(self, endpoint, request_timeout):
            pass

        def get_endpoint_config(self):
            return {
                "id": "openai-chat",
                "endpoint_type": "llm/v2/chat",
                "model": {
                    "provider": "openai",
                    "name": "gpt-4o-mini-2024-07-18",
                    "input_cost_1k_tokens": 0.00015,
                    "output_cost_1k_tokens": 0.0006,
                    "token_limit": 128000,
                    "config": {
                        "stratio_credential": "openai-token",
                        "openai_api_type": "openai",
                        "openai_api_base": "https://api.openai.com/v1",
                    },
                },
            }

        @staticmethod
        def predict(inputs):
            choices = []
            for i in range(n):
                choice = {
                    "index": i,
                    "message": {
                        "role": "assistant",
                        "content": msg_output,
                    },
                    "finish_reason": "stop",
                }
                choices.append(choice)

            return {
                "id": "chatcmpl-9H7eftpAsArNVo3xKrky80sXJaAhy",
                "object": "chat.completion",
                "created": 1713868029,
                "model": "gpt-3.5-turbo-0125",
                "choices": choices,
                "usage": {
                    "prompt_tokens": 16,
                    "completion_tokens": 41,
                    "total_tokens": 57,
                },
            }

    mocker.patch(
        "genai_core.chat_models.stratio_chat.GatewayClient",
        MockGatewayClient,
    )


class TestGatewayChain:
    def test_chain(self, mocker: MockerFixture):
        msg_output = "Why did the dog sit in the shade?\n\nBecause he didn't want to be a hot dog!"
        n = 1
        mock_gateway(mocker, msg_output, n)

        genai_chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=n,
            json_format=False,
        )
        chain = genai_chain.chain()
        result = chain.invoke({"topic": "dogs"})

        assert len(result.generations[0]) == 1
        assert result.generations[0][0].message.content == msg_output

    def test_chain_with_json_format(self, mocker: MockerFixture):
        msg_output = (
            '{\n  "joke": "Why did the car break up with the mechanic? It just couldn\'t handle the '
            'pressure."\n}'
        )
        n = 1
        mock_gateway(mocker, msg_output, n)

        genai_chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=n,
            json_format=True,
        )
        chain = genai_chain.chain()
        result = chain.invoke({"topic": "cars"})

        assert len(result.generations[0]) == 1
        assert result.generations[0][0].message.content == msg_output

    def test_chain_with_multiple_messages(self, mocker: MockerFixture):
        msg_output = "Why did the dog sit in the shade?\n\nBecause he didn't want to be a hot dog!"
        n = 2
        mock_gateway(mocker, msg_output, n)

        genai_chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=n,
            json_format=False,
        )
        chain = genai_chain.chain()
        result = chain.invoke({"topic": "dogs"})

        assert len(result.generations[0]) == 2
        assert result.generations[0][0].message.content == msg_output


if __name__ == "__main__":
    pytest.main()
