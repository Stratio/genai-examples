"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from abc import ABC
from typing import Optional

from genai_core.chain.base import BaseGenAiChain, GenAiChainParams
from genai_core.logger.logger import log
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from prometheus_client import Gauge


class MetricsChain(BaseGenAiChain, ABC):
    def __init__(self):
        self.metric_invoke_counter: Optional[Gauge] = None
        log.info("Chain Metrics ready!")

    def chain(self) -> Runnable:
        def increase_metric(data: dict) -> dict:
            self.metric_invoke_counter.labels("value1").inc()
            return data

        chain = (
            RunnablePassthrough()
            | {"input": RunnablePassthrough()}
            | RunnableLambda(increase_metric)
        )
        return chain

    def init_metrics(self):
        self.metric_invoke_counter = Gauge(
            "invoke_counter",
            "Number of requests to the invoke method.",
            labelnames=("label1",),
        )

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
