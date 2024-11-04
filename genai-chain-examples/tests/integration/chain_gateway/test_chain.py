"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import json

import pytest

from genai_core.test.pytest_utils import setup_test_envs

from genai_chain_gateway.chain import GatewayChain


def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except ValueError:
        return False


class TestGatewayChain:
    def test_chain(self, setup_test_envs):
        chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=1,
            json_format=False,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke({"topic": "dogs"})

        assert len(result.generations[0]) == 1
        assert "dog" in result.generations[0][0].text
        assert "dog" in result.generations[0][0].message.content.lower()

    def test_chain_with_multiple_messages(self, setup_test_envs):
        chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=2,
            json_format=False,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke({"topic": "dogs"})

        assert len(result.generations[0]) == 2
        assert "dog" in result.generations[0][0].message.content.lower()
        assert "dog" in result.generations[0][1].message.content.lower()
        assert "dog" in result.generations[0][0].text
        assert "dog" in result.generations[0][1].text

    def test_chain_with_json_format(self, setup_test_envs):
        chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=1,
            json_format=True,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke({"topic": "dogs"})

        assert len(result.generations[0]) == 1
        assert "dog" in result.generations[0][0].message.content.lower()
        assert "dog" in result.generations[0][0].text
        assert is_valid_json(result.generations[0][0].message.content)
        assert is_valid_json(result.generations[0][0].text)

    def test_chain_with_json_format_and_multiple_messages(self, setup_test_envs):
        chain = GatewayChain(
            chat_temperature=0.5,
            request_timeout=30,
            n=2,
            json_format=True,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke({"topic": "dogs"})

        assert len(result.generations[0]) == 2
        assert "dog" in result.generations[0][0].message.content.lower()
        assert "dog" in result.generations[0][1].message.content.lower()
        assert "dog" in result.generations[0][0].text
        assert "dog" in result.generations[0][1].text
        assert is_valid_json(result.generations[0][0].message.content)
        assert is_valid_json(result.generations[0][1].message.content)
        assert is_valid_json(result.generations[0][0].text)
        assert is_valid_json(result.generations[0][1].text)


if __name__ == "__main__":
    """
    Before running this script:
    1. Provide the env variables (see genai_chain_gateway/README.md)
    """
    pytest.main()
