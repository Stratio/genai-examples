"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import random

import pytest
from genai_chain_memory.chain import MemoryChain
from genai_core.test.pytest_utils import setup_test_envs

# borrar

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class TestMemoryChain:
    def test_invoke_chain(self, setup_test_envs):
        path = f"test_memory_{random.randint(1, 100)}"
        chain = MemoryChain(
            openai_stratio_credential="openai-token",
            chat_temperature=0.5,
            memory_path=path,
        )
        chain_dag = chain.chain()

        schema = chain_dag.input_schema.schema().get("properties")
        ivars = chain_dag.input_schema.schema()
        isch = chain_dag.get_input_schema()
        # assert chain_dag.input_schema.schema().get("properties") == 'truco'

        in_0 = chain_dag.invoke(
            {"input": {"topic": "cars", "question": "brakes"}},
            {"configurable": {"session_id": "test"}},
        )

        assert len(in_0.content) > 0
        assert "car" in in_0.content.lower()

    def test_memory_chain(self, setup_test_envs):
        path = f"test_memory_{random.randint(1, 100)}"
        chain = MemoryChain(
            openai_stratio_credential="openai-token",
            chat_temperature=0.5,
            memory_path=path,
        )
        chain_dag = chain.chain()

        schema = chain_dag.input_schema.schema().get("properties")
        ivars = chain_dag.input_schema.schema()
        isch = chain_dag.get_input_schema()
        # assert chain_dag.input_schema.schema().get("properties") == 'truco'

        in_0 = chain_dag.invoke(
            {"topic": "cars", "input": "brakes"},
            {"configurable": {"session_id": "test"}},
        )

        assert len(in_0.content) > 0
        assert "car" in in_0.content.lower()

        in_1 = chain_dag.invoke(
            {"topic": "cars", "input": "what are the best?"},
            {"configurable": {"session_id": "test"}},
        )

        assert len(in_1.content) > 0
        assert "car" in in_1.content.lower()

    def test_promt_schema(self, setup_test_envs):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant about {topic}. \
                Your mission is to guide users from zero knowledge to understanding the fundamentals of {topic}. \
                Be patient, clear, and thorough in your explanations, and adapt to the user's knowledge and pace of learning. \
                Do not use synonyms to refer the {topic}",
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                ("human", "{input}"),
            ]
        )
        schema = prompt.input_variables
        assert prompt.input_variables == ["input", "topic"]


if __name__ == "__main__":
    """
    Before running this script:
    1. Execute `docker-compose up -d`
    2. Execute `scripts/load_vault_secrets.py`
    """
    pytest.main()
