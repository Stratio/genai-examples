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

from genai_chain_echo.chain import EchoChain


class TestEchoChain:
    def test_chain_input_schema(self, setup_test_envs):
        genai_chain = EchoChain()
        chain = genai_chain.chain()

        assert chain.input_schema.schema() == {"title": "RunnablePassthroughInput"}

    def test_chain_config_schema(self, setup_test_envs):
        genai_chain = EchoChain()
        chain = genai_chain.chain()

        assert chain.config_schema().schema() == {
            "properties": {},
            "title": "RunnableSequenceConfig",
            "type": "object",
        }

    def test_chain_output_schema(self, setup_test_envs):
        genai_chain = EchoChain()
        chain = genai_chain.chain()

        assert chain.output_schema().schema() == {
            "title": "format_output_output",
            "type": "string",
        }

    def test_chain_params(self, setup_test_envs):
        genai_chain = EchoChain()

        params = genai_chain.chain_params()
        assert params.audit_input_fields == ["*"]
        assert params.audit_output_fields == ["*"]
        assert params.extra_params is None

    def test_chain_invoke(self, setup_test_envs):
        genai_chain = EchoChain()
        chain = genai_chain.chain()
        result = chain.invoke("hello")

        assert result == "Input was: hello"

    @pytest.mark.asyncio
    async def test_chain_ainvoke(self, setup_test_envs):
        genai_chain = EchoChain()
        chain = genai_chain.chain()
        result = await chain.ainvoke("hello")

        assert result == "Input was: hello"


if __name__ == "__main__":
    pytest.main()
