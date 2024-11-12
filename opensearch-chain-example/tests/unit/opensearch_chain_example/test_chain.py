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

from opensearch_chain_example.chain import OpensourceChain


class TestOpensearchChain:

    def test_chain(self, setup_test_envs):
        chain = OpensourceChain(
            opensearch_url="https://opensearch.s000001-genai.k8s.fifteen.labs.stratio.com:9200",
            opensearch_min_score=30
        )
        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {
                    "search_value":"Scott",
                    "collection_name":"semantic_banking_customer_product360",
                    "table_value":"customer",
                    "column_value":"Full_Name"
            }
        )

        assert "neerc" in result.mad_hutter_riddle


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
    
    GenAI API service name
    GENAI_API_SERVICE_NAME=genai-api-qa3.s000001-genai
    """
    pytest.main()