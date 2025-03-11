"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

from genai_core.services.virtualizer.virtualizer_service import VirtualizerData
from langchain_core.runnables.config import RunnableConfig
import pytest
import random
import string

from pytest_mock import MockerFixture
from virtualizer_chain.chain import VirtualizerChain


def random_name() -> str:
    return "".join(random.choices(string.ascii_letters, k=10))


class VirtualizerMock:
    # Mock of virtualizer service with `data_query` method that just echoes the query

    def data_query(self, query: str):
        return VirtualizerData(data=[query], successful=True)


def test_execute_query_impersonated(mocker: MockerFixture):
    # This tests checks that the query sent to virtualizer is impersonated with the `EXECUTE AS`
    # we patch our chain so that it uses our Virtualizer mock service that just returns the query
    mocker.patch(
        "virtualizer_chain.chain.VirtualizerChain._init_virtualizer",
        return_value=VirtualizerMock(),
    )

    # instantiate the chain
    chain = VirtualizerChain("virtualizer_host", 0)

    # define the input with the query
    query = "select 1 as id"
    chain_input = {"query": query}

    # Also, we add the configuration with the auth metadata that is added by genai api when running
    # normally. For the user id we just use a random name
    user = random_name()
    chain_config = RunnableConfig(
        metadata={
            "__genai_state": {
                "client_auth_type": "mtls",
                "client_user_id": user,
                "client_tenant": "tenant",
            }
        }
    )

    # execute the chain
    result = chain.chain().invoke(chain_input, chain_config)

    # assert that we have added the impersonation to the query
    assert result["query_result"][0] == f"EXECUTE AS {user} {query}"


if __name__ == "__main__":
    pytest.main()
