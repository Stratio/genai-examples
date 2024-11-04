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
from opensearchpy import TransportError

from genai_chain_docs.chain import DocsChain


class TestDocsChain:
    def test_chain_with_embedding_model_id(self, setup_test_envs):
        chain = DocsChain(
            opensearch_url="http://127.0.0.1:9200",
            opensearch_index="adif-rag",
            opensearch_embedding_model_id="XWKhQI0ByBgv0lA_wEXD",
            opensearch_use_ssl=False,
            openai_stratio_credential="openai-token",
            chat_temperature=0.0,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke("que es el arco eléctrico?")

        assert len(result) > 0
        assert "arco eléctrico" in result["answer"].lower()

    def test_chain(self, setup_test_envs):
        chain = DocsChain(
            opensearch_url="http://127.0.0.1:9200",
            opensearch_index="adif-rag",
            opensearch_use_ssl=False,
            openai_stratio_credential="openai-token",
            chat_temperature=0.0,
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke("que es el arco eléctrico?")

        assert len(result) > 0
        assert "arco eléctrico" in result["answer"].lower()

    def test_chain_error_model_not_found(self, setup_test_envs):
        chain = DocsChain(
            opensearch_url="http://127.0.0.1:9200",
            opensearch_index="adif-rag",
            opensearch_embedding_model_id="model_not_found",
            opensearch_use_ssl=False,
            openai_stratio_credential="openai-token",
            chat_temperature=0.0,
        )
        chain_dag = chain.chain()

        with pytest.raises(TransportError) as exc_info:
            chain_dag.invoke("que es el arco eléctrico?")

        exception = exc_info.value

        assert "model not loaded" in str(exception)


if __name__ == "__main__":
    """
    Before running this script:
    1. Execute `docker-compose up -d`
    2. Execute `scripts/load_vault_secrets.py`
    If you want to connect to a remote OpenSearch instance:
    3. Configure and load the certificates in `scripts/load_vault_secrets.py`
    4. Port forward the OpenSearch port with `scripts/start-tunnel.sh`
    5. Add `os-genai.s000001-genai` in your `/etc/hosts` file
    6. Set `opensearch_use_ssl` to `True`
    7. Set `opensearch_url` to `https://os-genai.s000001-genai:19200`
    """
    pytest.main()
