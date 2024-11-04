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

from genai_core.test.pytest_utils import setup_test_envs
from genai_chain_joke.chain import JokeChain


class TestJokeChain:
    def test_chain(self, setup_test_envs):
        chain = JokeChain(
            openai_stratio_credential="openai-token",
            chat_temperature=0.5,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke({"topic": "dogs"})

        assert len(result.content) > 0
        assert "dog" in result.content.lower()


if __name__ == "__main__":
    """
    Before running this script:
    1. Execute `docker-compose up -d`
    2. Execute `scripts/load_vault_secrets.py`
    """
    pytest.main()
