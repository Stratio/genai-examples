"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from typing import Optional, Any

from genai_core.chain.base import BaseGenAiChain
from genai_core.clients.vault.vault_client import VaultClient
from genai_core.logger.logger import log
from genai_core.vectorstores.opensearch_ml_vector_search import (
    OpenSearchMlVectorSearch,
)

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI


RETRIEVER_KEY = "retriever"
CONTEXT_KEY = "context"
INPUT_KEY = "question"
LLM_RESPONSE_KEY = "model_response"


class DocsChain(BaseGenAiChain):
    def __init__(
        self,
        opensearch_url: str,
        opensearch_index: str,
        opensearch_embedding_model_id: Optional[str] = None,
        opensearch_use_ssl: bool = True,
        openai_stratio_credential: str = "openai-token",
        chat_temperature: float = 0.0,
        show_references: bool = True,
    ):
        vault_client = VaultClient()

        # opensearch config
        self.opensearch_url = opensearch_url
        self.opensearch_index = opensearch_index
        self.embedding_model_id = opensearch_embedding_model_id
        self.opensearch_use_ssl = opensearch_use_ssl
        self.client_cert_path = None
        self.client_key_path = None
        self.ca_cert_path = None
        if self.opensearch_use_ssl:
            (
                self.client_cert_path,
                self.client_key_path,
            ) = vault_client.get_service_certificate_pem_paths()
            self.ca_cert_path = vault_client.get_ca_bundle_pem_path()

        # openai config
        secret = vault_client.get_password(openai_stratio_credential)
        if "token" not in secret:
            raise ValueError(
                "The secret in Vault is malformed. It has to contain the 'token' field."
            )
        self.openai_api_key = secret["token"]
        self.openai_model = "gpt-3.5-turbo"
        self.chat_temperature = chat_temperature

        # chain config
        self.show_references = show_references

        log.info("Chain Docs ready!")

    @staticmethod
    def format_docs(context: dict) -> str:
        return "\n\n".join(doc.page_content for doc in context[RETRIEVER_KEY])

    def process_output(self, data: dict):
        model_response = data.get(LLM_RESPONSE_KEY, "")
        documents = data.get(RETRIEVER_KEY, [])

        if not self.show_references:
            return {"answer": model_response}

        result_references_dict: dict = {}

        for doc in documents:
            if not doc.metadata or (
                "document_title" not in doc.metadata
                and "document_uri" not in doc.metadata
                and "document_page" not in doc.metadata
            ):
                continue

            title = doc.metadata.get("document_title", "undefined")
            uri = doc.metadata.get("document_uri", "undefined")
            page = doc.metadata.get("document_page", "undefined")

            ref_key = title + uri
            if ref_key in result_references_dict:
                result_references_dict[ref_key]["document_pages"].append(page)
            else:
                result_references_dict[ref_key] = {
                    "document_title": title,
                    "document_uri": uri,
                    "document_pages": [page],
                }

        result_references = sorted(
            result_references_dict.values(),
            key=lambda x: (-len(x["document_pages"]), x["document_title"]),
        )

        response_dict = {
            "answer": model_response,
            "references": result_references,
        }

        return response_dict

    # pylint: disable=invalid-name
    def chain(self) -> Runnable:
        vector_store = OpenSearchMlVectorSearch(
            opensearch_url=self.opensearch_url,
            index_name=self.opensearch_index,
            embedding_model_id=self.embedding_model_id,
            use_ssl=self.opensearch_use_ssl,
            verify_certs=True,
            ca_certs=self.ca_cert_path,
            client_cert=self.client_cert_path,
            client_key=self.client_key_path,
        )
        retriever = vector_store.as_retriever()

        prompt = ChatPromptTemplate.from_template(
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to "
            "answer the question. If you don't know the answer, just say that you don't know. Use three sentences "
            "maximum and keep the answer concise. \n\nQuestion: {question} \n\nContext: {context} \n\nAnswer: \n"
        )

        chat_model = ChatOpenAI(
            openai_api_key=self.openai_api_key,
            model=self.openai_model,
            temperature=self.chat_temperature,
        )

        chain: Any = (
            RunnablePassthrough()
            | {
                RETRIEVER_KEY: retriever,
                INPUT_KEY: RunnablePassthrough(),
            }
            | RunnablePassthrough.assign(**{CONTEXT_KEY: self.format_docs})
            | RunnablePassthrough.assign(
                **{LLM_RESPONSE_KEY: prompt | chat_model | StrOutputParser()}
            )
            | RunnableLambda(self.process_output)
        )

        return chain
