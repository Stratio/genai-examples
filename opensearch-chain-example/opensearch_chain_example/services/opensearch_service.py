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


# TODO: move to genai_core
class OpenSearchService:
    """OpenSearch service to search values for parametric SQL generation"""

    def __init__(
        self,
        opensearch_url: str,
        ca_certs: Optional[str] = None,
        client_cert: Optional[str] = None,
        client_key: Optional[str] = None,
        **kwargs,
    ):
        self.client = OpenSearch(
            hosts=[opensearch_url],
            ca_certs=ca_certs,
            client_cert=client_cert,
            client_key=client_key,
            **kwargs,
        )

    @staticmethod
    def transform_index(index):
        return index.lower()

    def search_filter_values(
        self,
        index: str,
        table_value: str,
        column_value: str,
        search_value: str,
        size=1,
        min_score=2,
    ) -> Optional[Dict[str, Any]]:
        """Search values on index for a given table and column"""
        try:
            transformed_index = self.transform_index(index)
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
            return self.client.search(index=transformed_index, body=query)
        except Exception as e:
            raise e
