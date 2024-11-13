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

from genai_core.logger.logger import log
from opensearch_chain_example.chain import OpensourceChain

SEARCH_VALUE_TEST_MOCK = "Scott"
TABLE_VALUE_TEST_MOCK = "customer"
COLUMN_VALUE_TEST_MOCK = "Full_Name"
COLLECTION_VALUE_TEST_MOCK = "semantic_banking_customer_product360"
SEARCH_FILTER_TEST_MOCK = "Scott Pillgrim"


def mock_init_opensearch_service(mocker):
    mocker.patch(
        "opensearchpy.client.indices.IndicesClient.get_alias",
        return_value={"index": "alias"},
    )


class OpenSearchServiceMock:
    "Mock of OpenSearch serivce with `search_filter_values` method that just echoes the query"

    def search_filter_values(
        self,
        index: str,
        table_value: str,
        column_value: str,
        search_value: str,
        size=1,
        min_score=2,
    ):
        result = (
            {
                "hits": {
                    "hits": [
                        {"_source": {"value": SEARCH_FILTER_TEST_MOCK}},
                    ]
                }
            }
            if search_value == SEARCH_VALUE_TEST_MOCK
            else {"hits": {"hits": []}}
        )
        return result


class TestOpensearchChain:
    def test_chain(self, mocker):
        # we patch our chain so that it uses our OpenSearch mock service that just returns the query
        mocker.patch(
            "opensearch_chain_example.chain.OpensourceChain._init_opensearch",
            return_value=OpenSearchServiceMock(),
        )

        chain = OpensourceChain(
            opensearch_url="mock",
            opensearch_min_score=30,
        )

        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {
                "search_value": SEARCH_VALUE_TEST_MOCK,
                "collection_name": COLLECTION_VALUE_TEST_MOCK,
                "table_value": TABLE_VALUE_TEST_MOCK,
                "column_value": COLUMN_VALUE_TEST_MOCK,
            }
        )
        log.info(result)
        assert (
            f"To obtain the requested value '{SEARCH_VALUE_TEST_MOCK}' in the column '{COLUMN_VALUE_TEST_MOCK}' of the table  '{TABLE_VALUE_TEST_MOCK}', the exact value to filter is '{SEARCH_FILTER_TEST_MOCK}'."
            == result["opensearch_explanation"]
        )

    def test_chain_no_filters(self, mocker):
        # we patch our chain so that it uses our OpenSearch mock service that just returns the query
        mocker.patch(
            "opensearch_chain_example.chain.OpensourceChain._init_opensearch",
            return_value=OpenSearchServiceMock(),
        )

        chain = OpensourceChain(
            opensearch_url="mock",
            opensearch_min_score=30,
        )

        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {
                "search_value": "NotScott",
                "collection_name": COLLECTION_VALUE_TEST_MOCK,
                "table_value": TABLE_VALUE_TEST_MOCK,
                "column_value": COLUMN_VALUE_TEST_MOCK,
            }
        )
        log.info(result)
        assert f"No parametric filter found." == result["opensearch_explanation"]


if __name__ == "__main__":
    pytest.main()
