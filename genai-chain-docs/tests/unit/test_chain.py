"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
from typing import List

import pytest

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.runnables import Runnable
from pytest_mock import MockerFixture

from genai_chain_docs.chain import DocsChain


def mock_vault(mocker: MockerFixture, password: dict) -> None:
    mocker.patch(
        "genai_core.clients.vault.vault_client.VaultClient.__init__", lambda x: None
    )
    mocker.patch(
        "genai_core.clients.vault.vault_client.VaultClient.get_password",
        return_value=password,
    )


def get_test_chain(show_references) -> Runnable:
    chain_doc = DocsChain(
        opensearch_url="dummy_url",
        opensearch_index="dummy_index",
        opensearch_embedding_model_id="dummy_embedding_model_id",
        show_references=show_references,
        opensearch_use_ssl=False,
        openai_stratio_credential="dummy_credential",
        chat_temperature=0.0,
    )
    return chain_doc.chain()


class TestDocsChain:
    @pytest.fixture
    def setup_class(self, mocker):
        self.msg_input = "Cuéntame sobre los mamíferos"
        self.msg_output = (
            "Los mamíferos son animales vertebrados de sangre caliente, que se "
            "caracterizan por tener glándulas mamarias, con las que producen leche "
            "para alimentar a sus crías. Los perros y leones son mamíferos, siendo"
            "los perros mamífero carnívoro/omnívoro depredador de la familia de los "
            "cánidos, es una subespecie del lobo (Canis lupus)"
        )
        mock_vault(mocker, password={"token": "test-token"})

        self.mocker_chat_model = mocker.patch(
            "langchain_core.language_models.chat_models.BaseChatModel.invoke",
        )
        self.mocker_chat_model.return_value = AIMessage(content=str(self.msg_output))

        self.mocker_similarity_search = mocker.patch(
            "genai_core.vectorstores.opensearch_ml_vector_search.OpenSearchMlVectorSearch.similarity_search"
        )

    def test_chain_show_references(self, mocker, setup_class):
        references = [
            {
                "document_title": "document_title_perros",
                "document_uri": "document_title_perros.pdf",
                "document_pages": [6, 21],
            },
            {
                "document_title": "document_title_leones",
                "document_uri": "document_title_leones.pdf",
                "document_pages": [7],
            },
            {
                "document_title": "document_title_mamiferos",
                "document_uri": "document_title_mamiferos.pdf",
                "document_pages": [9],
            },
        ]

        self.prompt = (
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to "
            "answer the question. If you don't know the answer, just say that you don't know. Use three sentences "
            f"maximum and keep the answer concise. \n\nQuestion: {self.msg_input} \n\nContext: Los perros son "
            "mamíferos.\n\nLos perros son mamífero carnívoro/omnívoro depredador de la familia de los cánidos, es "
            "una subespecie del lobo (Canis lupus)\n\nLos leones son mamíferos.\n\nLos mamíferos son animales "
            "vertebrados de sangre caliente, que se caracterizan por tener glándulas mamarias, con las que "
            "producen leche para alimentar a sus crías. \n\nAnswer: \n"
        )

        self.mocker_similarity_search.return_value = get_mock_documents()

        chain_doc = get_test_chain(True)

        result = chain_doc.invoke(self.msg_input)

        assert result["answer"] == self.msg_output
        assert result["references"] == references

        self.mocker_similarity_search.assert_called_once_with(mocker.ANY)

        self.mocker_chat_model.assert_called_once_with(
            ChatPromptValue(messages=[HumanMessage(content=self.prompt)]),
            mocker.ANY,
        )

    def test_chain_show_references_without_references(self, mocker, setup_class):
        references = []

        self.prompt = (
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to "
            "answer the question. If you don't know the answer, just say that you don't know. Use three sentences "
            f"maximum and keep the answer concise. \n\nQuestion: {self.msg_input} \n\nContext:  \n\nAnswer: \n"
        )

        self.mocker_similarity_search.return_value = references

        chain_doc = get_test_chain(True)

        result = chain_doc.invoke(self.msg_input)

        assert result["answer"] == self.msg_output
        assert result["references"] == references

        self.mocker_similarity_search.assert_called_once_with(mocker.ANY)

        self.mocker_chat_model.assert_called_once_with(
            ChatPromptValue(messages=[HumanMessage(content=self.prompt)]),
            mocker.ANY,
        )

    def test_chain_not_show_references(self, mocker, setup_class):
        self.prompt = (
            "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to "
            "answer the question. If you don't know the answer, just say that you don't know. Use three sentences "
            f"maximum and keep the answer concise. \n\nQuestion: {self.msg_input} \n\nContext: Los perros son "
            "mamíferos.\n\nLos perros son mamífero carnívoro/omnívoro depredador de la familia de los cánidos, es "
            "una subespecie del lobo (Canis lupus)\n\nLos leones son mamíferos.\n\nLos mamíferos son animales "
            "vertebrados de sangre caliente, que se caracterizan por tener glándulas mamarias, con las que "
            "producen leche para alimentar a sus crías. \n\nAnswer: \n"
        )

        self.mocker_similarity_search.return_value = get_mock_documents()

        chain_doc = get_test_chain(False)

        result = chain_doc.invoke(self.msg_input)

        assert result["answer"] == self.msg_output
        assert "references" not in result

        self.mocker_similarity_search.assert_called_once_with(mocker.ANY)

        self.mocker_chat_model.assert_called_once_with(
            ChatPromptValue(messages=[HumanMessage(content=self.prompt)]),
            mocker.ANY,
        )

    def test_chain_input_schema(self, mocker):
        mock_vault(mocker, password={"token": "test-token"})
        chain = get_test_chain(True)

        assert chain.input_schema.schema() == {"title": "RunnablePassthroughInput"}

    def test_chain_config_schema(self, mocker):
        mock_vault(mocker, password={"token": "test-token"})
        chain = get_test_chain(True)

        assert chain.config_schema().schema() == {
            "properties": {},
            "title": "RunnableSequenceConfig",
            "type": "object",
        }

    def test_chain_output_schema(self, mocker):
        mock_vault(mocker, password={"token": "test-token"})
        chain = get_test_chain(True)

        assert chain.output_schema().schema() == {"title": "process_output_output"}

    def test_process_output(self, mocker):
        input_dict = {
            "retriever": [
                Document(
                    page_content="dummy_page_content_1",
                    metadata={
                        "document_title": "dummy_document_title_1",
                        "document_page": 6,
                        "document_uri": "dummy_document_title_1.pdf",
                    },
                ),
                Document(
                    page_content="dummy_page_content_2",
                    metadata={
                        "document_title": "dummy_document_title_2",
                        "document_page": 21,
                        "document_uri": "dummy_document_title_2.pdf",
                    },
                ),
            ],
            "question": "dummy_question",
            "context": "dummy_context",
            "model_response": "dummy_model_response",
        }

        mock_vault(mocker, password={"token": "test-token"})
        chain = DocsChain(
            opensearch_url="dummy_url",
            opensearch_index="dummy_index",
            opensearch_embedding_model_id="dummy_embedding_model_id",
            opensearch_use_ssl=False,
            openai_stratio_credential="dummy_credential",
            chat_temperature=0.0,
        )
        result = chain.process_output(input_dict)

        assert "answer" in result
        assert "references" in result
        assert len(result["references"]) == len(input_dict["retriever"])

    def test_process_output_without_retriever(self, mocker):
        input_dict = {
            "question": "dummy_question",
            "context": "dummy_context",
            "model_response": "dummy_model_response",
        }

        mock_vault(mocker, password={"token": "test-token"})
        chain = DocsChain(
            opensearch_url="dummy_url",
            opensearch_index="dummy_index",
            opensearch_embedding_model_id="dummy_embedding_model_id",
            opensearch_use_ssl=False,
            openai_stratio_credential="dummy_credential",
            chat_temperature=0.0,
        )
        result = chain.process_output(input_dict)

        assert "answer" in result
        assert "references" in result
        assert len(result["references"]) == 0

    def test_process_output_with_retriever_with_metadata_without_document_page(
        self, mocker
    ):
        input_dict = {
            "retriever": [
                Document(
                    page_content="dummy_page_content_1",
                    metadata={
                        "document_title": "dummy_document_title_1",
                        "document_uri": "dummy_document_title_1.pdf",
                    },
                ),
                Document(
                    page_content="dummy_page_content_2",
                    metadata={
                        "document_title": "dummy_document_title_2",
                        "document_uri": "dummy_document_title_2.pdf",
                    },
                ),
            ],
            "question": "dummy_question",
            "context": "dummy_context",
            "model_response": "dummy_model_response",
        }

        mock_vault(mocker, password={"token": "test-token"})
        chain = DocsChain(
            opensearch_url="dummy_url",
            opensearch_index="dummy_index",
            opensearch_embedding_model_id="dummy_embedding_model_id",
            opensearch_use_ssl=False,
            openai_stratio_credential="dummy_credential",
            chat_temperature=0.0,
        )
        result = chain.process_output(input_dict)

        assert "answer" in result
        assert "references" in result
        assert len(result["references"]) == 2
        assert result["references"][0]["document_pages"][0] == "undefined"

    def test_process_output_with_retriever_with_metadata_without_anything(self, mocker):
        input_dict = {
            "retriever": [
                Document(
                    page_content="dummy_page_content_1",
                    metadata={
                        "other_field": "other_field_1",
                    },
                ),
                Document(
                    page_content="dummy_page_content_2",
                    metadata={
                        "other_field": "other_field_2",
                    },
                ),
            ],
            "question": "dummy_question",
            "context": "dummy_context",
            "model_response": "dummy_model_response",
        }

        mock_vault(mocker, password={"token": "test-token"})
        chain = DocsChain(
            opensearch_url="dummy_url",
            opensearch_index="dummy_index",
            opensearch_embedding_model_id="dummy_embedding_model_id",
            opensearch_use_ssl=False,
            openai_stratio_credential="dummy_credential",
            chat_temperature=0.0,
        )
        result = chain.process_output(input_dict)

        assert "answer" in result
        assert "references" in result
        assert len(result["references"]) == 0

    def test_process_output_with_retriever_without_metadata(self, mocker):
        input_dict = {
            "retriever": [
                Document(
                    page_content="dummy_page_content_1",
                ),
                Document(
                    page_content="dummy_page_content_2",
                ),
            ],
            "question": "dummy_question",
            "context": "dummy_context",
            "model_response": "dummy_model_response",
        }

        mock_vault(mocker, password={"token": "test-token"})
        chain = DocsChain(
            opensearch_url="dummy_url",
            opensearch_index="dummy_index",
            opensearch_embedding_model_id="dummy_embedding_model_id",
            opensearch_use_ssl=False,
            openai_stratio_credential="dummy_credential",
            chat_temperature=0.0,
        )
        result = chain.process_output(input_dict)

        assert "answer" in result
        assert "references" in result
        assert len(result["references"]) == 0


def get_mock_documents() -> List[Document]:
    return [
        Document(
            page_content="Los perros son mamíferos.",
            metadata={
                "document_title": "document_title_perros",
                "document_page": 6,
                "document_uri": "document_title_perros.pdf",
            },
        ),
        Document(
            page_content="Los perros son mamífero carnívoro/omnívoro depredador de la "
            "familia de los cánidos, es una subespecie del lobo (Canis lupus)",
            metadata={
                "document_title": "document_title_perros",
                "document_page": 21,
                "document_uri": "document_title_perros.pdf",
            },
        ),
        Document(
            page_content="Los leones son mamíferos.",
            metadata={
                "document_title": "document_title_leones",
                "document_page": 7,
                "document_uri": "document_title_leones.pdf",
            },
        ),
        Document(
            page_content="Los mamíferos son animales vertebrados de sangre caliente, que se "
            "caracterizan por tener glándulas mamarias, con las que producen leche "
            "para alimentar a sus crías.",
            metadata={
                "document_title": "document_title_mamiferos",
                "document_page": 9,
                "document_uri": "document_title_mamiferos.pdf",
            },
        ),
    ]


if __name__ == "__main__":
    pytest.main()
