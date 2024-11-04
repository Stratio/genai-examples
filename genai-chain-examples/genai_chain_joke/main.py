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
        module_name="genai_chain_joke.chain",
        class_name="JokeChain",
        config={"openai_stratio_credential": "openai-token", "chat_temperature": 0.5},
    )
    app.start_server()


if __name__ == "__main__":
    """
    Before running this script:
    1. Execute `docker-compose up -d`
    2. Execute `scripts/load_vault_secrets.py`
    """
    main()
