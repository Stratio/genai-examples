"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import os

import pytest

from genai_core.test.pytest_utils import setup_test_envs

from opensearch_chain_example.chain import OpensourceChain


class TestBasicActorChain:
    def test_chain_english(self, setup_test_envs):
        chain = OpensourceChain(
            opensearch_url=os.getenv("OPENSEARCH_URL"),
            opensearch_min_score=10
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke({"user_request": "Hi! Nice to meet you! Where's the Queen of Hearts?"})

        assert "roses" in result.mad_hutter_riddle

if __name__ == "__main__":
    """
    Before running this script, you should configure the following environment variables:
    variables needed to tell the VaulClient where to find the certificates so it does not need to
    actually access any Vault. You can obtain your certificates from your profile in Gosec
    VAULT_LOCAL_CLIENT_CERT=/path/to/cert.crt
    VAULT_LOCAL_CLIENT_KEY=/path/to/private-key.key
    VAULT_LOCAL_CA_CERTS=/path/to/ca-cert.crt

    Opensearch service URL
    OPENSEARCH_URL=https://opensearch.s000001-genai.k8s.fifteen.labs.stratio.com:9200
    """
    pytest.main()
