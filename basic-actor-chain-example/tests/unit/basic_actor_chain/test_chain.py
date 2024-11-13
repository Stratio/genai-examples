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

USER_REQUEST_EXPLANATION = (
    "The user is asking about the location of the Queen of Hearts in Wonderland."
)
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

        assert USER_REQUEST_EXPLANATION == result.user_request_explanation
        assert MAD_HUTTER_RIDDLE == result.mad_hutter_riddle
        assert MESSAGE == result.message


if __name__ == "__main__":
    pytest.main()
