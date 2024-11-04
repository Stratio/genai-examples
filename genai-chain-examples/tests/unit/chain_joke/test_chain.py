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

from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompt_values import ChatPromptValue
from pytest_mock import MockerFixture

from genai_chain_joke.chain import JokeChain


def mock_vault(mocker: MockerFixture, password: dict) -> None:
    mocker.patch(
        "genai_core.clients.vault.vault_client.VaultClient.__init__", lambda x: None
    )
    mocker.patch(
        "genai_core.clients.vault.vault_client.VaultClient.get_password",
        return_value=password,
    )


def mock_chat_messages(mocker: MockerFixture, messages: list[tuple[str, str]]) -> None:
    # noinspection PyUnusedLocal
    def chat_invoke(chat_model, chat_prompt: ChatPromptValue, config) -> BaseMessage:
        input_msg = chat_prompt.messages[0].content
        for msg, output in messages:
            if msg == input_msg:
                return AIMessage(content=output)
        raise ValueError(f"Unexpected input: {input_msg}")

    mocker.patch(
        "langchain_core.language_models.chat_models.BaseChatModel.invoke", chat_invoke
    )


class TestJokeChain:
    def test_chain(self, mocker: MockerFixture):
        mock_vault(mocker, password={"token": "test-token"})
        msg_input = "tell me a joke about dogs"
        msg_output = "Why did the dog sit in the shade?\n\nBecause he didn't want to be a hot dog!"
        mock_chat_messages(
            mocker,
            messages=[
                (
                    msg_input,
                    msg_output,
                )
            ],
        )

        genai_chain = JokeChain(
            openai_stratio_credential="openai-token",
            chat_temperature=0.5,
        )
        chain = genai_chain.chain()
        result = chain.invoke({"topic": "dogs"})

        assert result.content == msg_output


if __name__ == "__main__":
    pytest.main()
