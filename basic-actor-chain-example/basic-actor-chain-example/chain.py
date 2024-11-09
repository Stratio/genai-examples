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
from genai_core.chat_models.stratio_chat import StratioGenAIGatewayChat
from genai_core.logger.logger import log
from genai_core.services.governance.metadata_service import MetadataService
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda
from .actors.basic_actor import BasicExampleActor

class BasicGatewayChain(BaseGenAiChain, ABC):
    # Actors
    basic_actor: BasicExampleActor

    # Service Helpers
    metadata_service: MetadataService

    # Internal chain
    _chain: Optional[Runnable] = None
    def __init__(
        self,
        chat_temperature: float = 0.5,
        request_timeout: int = 30,
        n: int = 1,
        json_format: bool = False,
    ):
        self.chat_temperature = chat_temperature
        self.request_timeout = request_timeout
        self.n = n
        self.json_format = json_format

        log.info("Basic Actor Example chain ready!")

    def chain(self) -> Runnable:
        extra_params = {}
        template = "tell me Mad Hutter: {topic}"
        if self.json_format:
            extra_params = {"response_format": {"type": "json_object"}}
            template += " in json format"

        # Gateway target URI is configured from environment variable
        model = StratioGenAIGatewayChat(
            endpoint="QA-openai-chat-gpt-4o-mini",
            temperature=self.chat_temperature,
            n=self.n,
            request_timeout=self.request_timeout,
            extra_params=extra_params,
        )

        prompt = ChatPromptTemplate.from_template(template)

        runnable_lambda = RunnableLambda(
            lambda topic: model.generate(messages=[prompt.format_messages(topic=topic)])
        )

        return runnable_lambda

    def chain_params(self) -> GenAiChainParams:
        return GenAiChainParams(audit_input_fields=["*"], audit_output_fields=["*"])
