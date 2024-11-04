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

from genai_core.chain.base import BaseGenAiChain, GenAiChainParams
from genai_core.logger.logger import log
from genai_core.runnables.genai_auth import GenAiAuthRunnable, GenAiAuth
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_core.runnables.utils import Input
from pydantic import BaseModel


class AuthOutput(BaseModel):
    input: Input = None
    auth: GenAiAuth = None
    is_auth: bool = None


def get_is_auth(data: dict) -> AuthOutput:
    out = AuthOutput(**data)
    out.is_auth = (
        out.auth.user_id == "admin" or out.auth.user_id_impersonated == "admin"
    )
    return out


class AuthChain(BaseGenAiChain, ABC):
    def __init__(self):
        log.info("Chain Auth ready!")

    def chain(self) -> Runnable:
        chain = (
            RunnablePassthrough()
            | {"input": RunnablePassthrough()}
            | RunnablePassthrough.assign(auth=GenAiAuthRunnable())
            | RunnableLambda(get_is_auth)
        )
        return chain

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
