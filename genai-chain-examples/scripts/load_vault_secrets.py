"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from genai_core.test.vault_utils import (
    create_mount_points,
    create_openai_secret_for_genai_gateway,
    create_openai_secret_for_genai_api,
)


def main() -> None:
    create_mount_points()
    create_openai_secret_for_genai_gateway("openai-token")
    create_openai_secret_for_genai_api("openai-token")
    print("Secrets created!")


if __name__ == "__main__":
    """
    Usage:
    - Set env var OPENAI_TOKEN = <your-openai-token>
    """
    main()
