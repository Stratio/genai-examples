"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from genai_core.server.server import GenAiServer


def main():
    app = GenAiServer(
        module_name="genai_chain_docs.chain",
        class_name="DocsChain",
        config={
            "opensearch_url": "http://127.0.0.1:9200",
            "opensearch_index": "adif-rag",
            "opensearch_use_ssl": False,
            "openai_stratio_credential": "openai-token",
            "chat_temperature": 0.0,
        },
    )
    app.start_server()


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
    main()
