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
        module_name="genai_chain_gateway.chain",
        class_name="GatewayChain",
        config={
            "chat_temperature": 0.5,
            "request_timeout": 30,
            "n": 2,
            "json_format": False,
        },
    )
    app.start_server()


if __name__ == "__main__":
    """
    Before running this script:
    1. Provide the env variables (see genai_chain_gateway/README.md)
    """
    main()
