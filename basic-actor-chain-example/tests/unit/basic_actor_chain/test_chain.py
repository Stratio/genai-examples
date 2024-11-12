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

from basic_actor_chain_example.chain import BasicActorChain


class TestBasicActorChain:
    def test_chain_english(self, setup_test_envs):
        chain = BasicActorChain(
            gateway_endpoint="QA-openai-chat-gpt-4o-mini", llm_timeout=100
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {"user_request": "Hi! Nice to meet you! Where's the Queen of Hearts?"}
        )

        assert "roses" in result.mad_hutter_riddle

    def test_chain_spanish(self, setup_test_envs):
        chain = BasicActorChain(
            gateway_endpoint="QA-openai-chat-gpt-4o-mini", llm_timeout=100
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {
                "user_request": "Hola! Encantada de conocerte! Sabes donde está la reina de corazones?"
            }
        )

        assert "rosas" in result.mad_hutter_riddle

    def test_chain_alice(self, setup_test_envs):
        chain = BasicActorChain(
            gateway_endpoint="QA-openai-chat-gpt-4o-mini", llm_timeout=100
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {
                "user_request": "Hola! Encantada de conocerte! Sabes donde está la reina de corazones?"
            },
            {
                "metadata": {
                    "__genai_state": {
                        "client_auth_type": "mtls",
                        "client_user_id": "Alice",
                        "client_tenant": "s000001"
                    }
                }
            }
        )

        assert "neerc" in result.mad_hutter_riddle


if __name__ == "__main__":
    """
    Before running this script, you should configure the following environment variables:
    1. Variables needed to access the Genai-Gateway (here we show an example with):
    GENAI_GATEWAY_URL=https://genai-developer-proxy-qa1-loadbalancer.s000001-genai.k8s.oscar.labs.stratio.com:8080/service/genai-gateway
    GENAI_GATEWAY_CLIENT_CERT=/path/to/user-cert.crt
    GENAI_GATEWAY_CLIENT_KEY=/path/to/user_private.key
    GENAI_GATEWAY_CA_CERTS=/path/to/ca-cert.crt
    """
    pytest.main()
