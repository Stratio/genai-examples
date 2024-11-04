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
from genai_core.runnables.genai_auth import GenAiAuth
from genai_core.test.pytest_utils import config_with_metadata
from genai_core.test.pytest_utils import setup_test_envs
from langchain_core.runnables import RunnableConfig
from genai_chain_auth.chain import AuthChain, AuthOutput


class TestAuthChain:
    def test_chain_input_schema(self, setup_test_envs):
        genai_chain = AuthChain()
        chain = genai_chain.chain()

        assert chain.input_schema.schema() == {"title": "RunnablePassthroughInput"}

    def test_chain_config_schema(self, setup_test_envs):
        genai_chain = AuthChain()
        chain = genai_chain.chain()

        assert chain.config_schema().schema() == {
            "properties": {},
            "title": "RunnableSequenceConfig",
            "type": "object",
        }

    def test_chain_output_schema(self, setup_test_envs):
        genai_chain = AuthChain()
        chain = genai_chain.chain()
        assert chain.output_schema().schema() == {
            "$defs": {
                "GenAiAuth": {
                    "description": "Model for GenAI authentication.\n\nAttributes:\n    "
                    "auth_type (Optional[str]): Authentication type.\n    "
                    "user_id (Optional[str]): User ID.\n    "
                    "user_id_impersonated (Optional[str]): Impersonated user ID.\n    "
                    "tenant (Optional[str]): Tenant.\n    "
                    "email (Optional[str]): Email.\n    "
                    "expiration (Optional[int]): Expiration.\n    "
                    "request_id (Optional[str]): Request ID.",
                    "properties": {
                        "auth_type": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Auth Type",
                        },
                        "user_id": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "User Id",
                        },
                        "user_id_impersonated": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "User Id Impersonated",
                        },
                        "tenant": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Tenant",
                        },
                        "email": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Email",
                        },
                        "expiration": {
                            "anyOf": [{"type": "integer"}, {"type": "null"}],
                            "default": None,
                            "title": "Expiration",
                        },
                        "request_id": {
                            "anyOf": [{"type": "string"}, {"type": "null"}],
                            "default": None,
                            "title": "Request Id",
                        },
                    },
                    "title": "GenAiAuth",
                    "type": "object",
                }
            },
            "properties": {
                "input": {"default": None, "title": "Input"},
                "auth": {"$ref": "#/$defs/GenAiAuth", "default": None},
                "is_auth": {"default": None, "title": "Is Auth", "type": "boolean"},
            },
            "title": "AuthOutput",
            "type": "object",
        }

    def test_chain_invoke(self, setup_test_envs, config_with_metadata: RunnableConfig):
        genai_chain = AuthChain()
        chain = genai_chain.chain()
        result: AuthOutput = chain.with_config(config_with_metadata).invoke(
            "Hello World!"
        )

        assert result.input == "Hello World!"
        assert result.auth == GenAiAuth(
            auth_type="mtls+impersonation",
            user_id="rocket.s000001-rocket",
            user_id_impersonated="admin",
            tenant="s000001",
            email="admin@fifteen.int",
            request_id="test-request-id",
            expiration=1705533628,
        )
        assert result.is_auth

    def test_chain_invoke_no_auth(self, setup_test_envs):
        genai_chain = AuthChain()
        chain = genai_chain.chain()
        result = chain.invoke("Hello World!")

        assert result.input == "Hello World!"
        assert result.auth == GenAiAuth()
        assert not result.is_auth


if __name__ == "__main__":
    pytest.main()
