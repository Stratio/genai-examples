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
    create_ca_bundle_certificate,
    create_openai_secret_for_genai_api,
    create_genai_api_service_certificate,
)


def main(opensearch_use_ssl: bool) -> None:
    create_mount_points()
    create_openai_secret_for_genai_api("openai-token")
    if opensearch_use_ssl:
        create_ca_bundle_certificate()
        create_genai_api_service_certificate()
    print("Secrets created!")


if __name__ == "__main__":
    """
    Usage:
    - Set env var OPENAI_TOKEN = <your-openai-token>
    If you want to connect to a remote OpenSearch instance you have to set up those env vars:
    - CLIENT_CERT_PATH=/home/.../genai-api.s000001-genai.pem
    - CLIENT_KEY_PATH=/home/.../genai-api.s000001-genai.key
    - CA_CERT_PATH=/home/.../ca-bundle.pem
    """
    main(opensearch_use_ssl=False)
