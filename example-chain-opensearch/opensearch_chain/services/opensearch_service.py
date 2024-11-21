"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from typing import Optional, Dict, Any

from opensearchpy import OpenSearch


class OpenSearchService:
    """
    OpenSearch service to interact with an OpenSearch service instance.
    """

    def __init__(
        self,
        opensearch_url: str,
        ca_certs: Optional[str] = None,
        client_cert: Optional[str] = None,
        client_key: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the OpenSearchService.

        Args:
            opensearch_url (str): The URL of the OpenSearch instance.
            ca_certs (Optional[str], optional): Path to CA certificates. Defaults to None.
            client_cert (Optional[str], optional): Path to client certificate. Defaults to None.
            client_key (Optional[str], optional): Path to client key. Defaults to None.
            **kwargs: Additional keyword arguments for the OpenSearch client.
        """
        self.client = OpenSearch(
            hosts=[opensearch_url],
            ca_certs=ca_certs,
            client_cert=client_cert,
            client_key=client_key,
            **kwargs,
        )

    def search_filter_values(
        self,
        index: str,
        table_value: str,
        column_value: str,
        search_value: str,
        size=1,
        min_score=2,
    ) -> Optional[Dict[str, Any]]:
        """
        Search values on index for a given table and column.

        This service should be adapted to the specific needs of your use case and the data indexed in the OpenSearch instance.

        Args:
            index (str): The index to search.
            table_value (str): The table value to search.
            column_value (str): The column value to search.
            search_value (str): The search value to filter.
            size (int, optional): The number of results to return. Defaults to 1.
            min_score (int, optional): The minimum score for results. Defaults to 2.

        Returns:
            Optional[Dict[str, Any]]: The search results, or raises an exception if an error occurs.
        """
        try:
            # Here you should adapt the query to your specific needs
            # In ths example, we assume that an external process created the index using the name of the database
            # and added documents by analyzing the data in the database and indexing the required columns with the following fields:
            # "table": the table name,
            # "column": the column name,
            # "value": the value of the column.
            # the query returns the first documents that matches the search value in a specific table and column
            query = {
                "size": size,
                "min_score": min_score,
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"table": table_value}},
                            {"term": {"column": column_value}},
                        ],
                        "should": [
                            {
                                "match": {
                                    "value": {
                                        "query": search_value,
                                        "fuzziness": "AUTO",
                                    }
                                }
                            }
                        ],
                    }
                },
            }
            return self.client.search(index=index, body=query)
        except Exception as e:
            raise e
