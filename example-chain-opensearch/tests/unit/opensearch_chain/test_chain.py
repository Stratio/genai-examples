"""
© 2025 Stratio Big Data Inc., Sucursal en España. All rights reserved.
This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""

import pytest

from opensearch_chain.chain import OpenSearchChain
from opensearch_chain.constants.constants import (
    OPENSEARCH_NO_RESULTS,
    OPENSEARCH_RESULT_KEY,
)

# Mock values for testing
SEARCH_VALUE_TEST_MOCK = "Scott"
TABLE_VALUE_TEST_MOCK = "customer"
COLUMN_VALUE_TEST_MOCK = "Full_Name"
COLLECTION_VALUE_TEST_MOCK = "semantic_banking_customer_product360"
SEARCH_FILTER_TEST_MOCK = "Scott Pillgrim"


def mock_init_opensearch_service(mocker):
    """
    Mock initialization of the OpenSearch service.

    Args:
        mocker: The mocker object used to patch methods.
    """
    mocker.patch(
        "opensearchpy.client.indices.IndicesClient.get_alias",
        return_value={"index": "alias"},
    )


class OpenSearchServiceMock:
    """
    Mock of OpenSearch service with `search_filter_values` method that returns a mock search result.
    """

    def search_filter_values(
        self,
        index: str,
        table_value: str,
        column_value: str,
        search_value: str,
        size=1,
        min_score=2,
    ):
        """
        Mock method to simulate search filter values in OpenSearch.

        SEARCH_FILTER_TEST_MOCK is returned if the search value is SEARCH_VALUE_TEST_MOCK.
        An empty list is returned otherwise.

        Args:
            index (str): The index to search.
            table_value (str): The table value to search.
            column_value (str): The column value to search.
            search_value (str): The search value to filter.
            size (int, optional): The number of results to return. Defaults to 1.
            min_score (int, optional): The minimum score for results. Defaults to 2.

        Returns:
            dict: A mock search result.
        """
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
    """
    Test suite for the OpenSearchChain class.
    """

    def test_chain(self, mocker):
        """
        Test the chain method with a search value that returns a value.

        Args:
            mocker: The mocker object used to patch methods.
        """
        # we patch our chain so that it uses our OpenSearch mock service that just returns the query
        mocker.patch(
            "opensearch_chain.chain.OpenSearchChain._init_opensearch",
            return_value=OpenSearchServiceMock(),
        )

        chain = OpenSearchChain(
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
        assert (
            f"For the requested search value '{SEARCH_VALUE_TEST_MOCK}' in the column '{COLUMN_VALUE_TEST_MOCK}' of the table  '{TABLE_VALUE_TEST_MOCK}', the first result is '{SEARCH_FILTER_TEST_MOCK}'."
            == result[OPENSEARCH_RESULT_KEY]
        )

    def test_chain_no_filters(self, mocker):
        """
        Test the chain method with a search value that returns no results.

        Args:
            mocker: The mocker object used to patch methods.
        """
        # we patch our chain so that it uses our OpenSearch mock service that just returns the query
        mocker.patch(
            "opensearch_chain.chain.OpenSearchChain._init_opensearch",
            return_value=OpenSearchServiceMock(),
        )

        chain = OpenSearchChain(
            opensearch_url="mock",
            opensearch_min_score=30,
        )

        chain_dag = chain.chain()
        result = chain_dag.invoke(
            {
                "search_value": f"Not{SEARCH_VALUE_TEST_MOCK}",
                "collection_name": COLLECTION_VALUE_TEST_MOCK,
                "table_value": TABLE_VALUE_TEST_MOCK,
                "column_value": COLUMN_VALUE_TEST_MOCK,
            }
        )
        assert OPENSEARCH_NO_RESULTS == result[OPENSEARCH_RESULT_KEY]


if __name__ == "__main__":
    pytest.main()
