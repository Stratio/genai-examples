"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import asyncio
import time
from abc import ABC

from genai_core.chain.base import BaseGenAiChain, GenAiChainParams
from genai_core.logger.logger import log
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda


class EchoChain(BaseGenAiChain, ABC):
    def __init__(self, response_delay: float = 0.0):
        self.response_delay = response_delay
        log.info("Chain Echo ready!")

    def chain(self) -> Runnable:
        def format_output(text: str) -> str:
            # this method is mandatory. it will be called by
            #  - invoke method
            #  - ainvoke method if the async method is not defined
            time.sleep(self.response_delay)
            return f"Input was: {text}"

        async def format_output_async(text: str) -> str:
            # this method is optional. if defined, it will be called by the ainvoke method
            await asyncio.sleep(self.response_delay)
            return f"Input was: {text}"

        chain = RunnablePassthrough() | RunnableLambda(
            format_output, afunc=format_output_async
        )
        return chain

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
