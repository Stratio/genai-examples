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

from basic_actor_chain_example.actors.basic_actor import (
    BasicExampleActor,
    BasicExampleActorOutput,
)
from basic_actor_chain_example.chain import BasicActorChain
from genai_core.test.mock_helper import mock_init_stratio_gateway, mock_actor

GATEWAY_ENDPOINT = "openai-chat"

USER_REQUEST_EXPLANATION = "The user is asking about the location of the Queen of Hearts in Wonderland."
MAD_HUTTER_RIDDLE = "In a garden of red, where the roses bloom, Who rules with a heart, and brings forth the doom? With a croquet mallet, she swings with delight, Where is she hiding, in day or in night?"
MESSAGE = "This riddle hints at the Queen of Hearts, known for her love of croquet and her fierce demeanor. The garden of roses symbolizes her domain, where she reigns with authority."

ACTOR_OUTPUT = BasicExampleActorOutput(
    user_request_explanation=USER_REQUEST_EXPLANATION,
    mad_hutter_riddle=MAD_HUTTER_RIDDLE,
    message=MESSAGE,
)


class TestBasicActorChain:
    @pytest.fixture
    def actor(self, mocker):
        mock_init_stratio_gateway(mocker)
        return BasicExampleActor(gateway_endpoint=GATEWAY_ENDPOINT)

    def test_chain(self, actor, mocker):
        mock_actor(mocker, actor.__class__, [[ACTOR_OUTPUT]])
        chain = BasicActorChain(gateway_endpoint=GATEWAY_ENDPOINT, llm_timeout=100)
        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {"user_request": "Hi! Nice to meet you! Where's the Queen of Hearts?"}
        )

        assert "roses" in result.mad_hutter_riddle


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
