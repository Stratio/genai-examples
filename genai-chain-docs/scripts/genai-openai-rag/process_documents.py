"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import glob
import os
from importlib import resources
import configparser
from typing import List

import requests
from langchain_community.document_loaders import PyPDFium2Loader
from langchain.text_splitter import RecursiveCharacterTextSplitter

OPENSEARCH_URL = ""
OPENSEARCH_CERT = ""
OPENSEARCH_CA = ""


def delete_all_documents(opensearch_index: str):
    print(f"Deleting all documents in index {opensearch_index} ...")
    url = f"{OPENSEARCH_URL}/{opensearch_index}/_delete_by_query"
    query = {"query": {"match_all": {}}}
    response = requests.post(
        url, json=query, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200


def index_document(opensearch_index: str, opensearch_document: dict):
    url = f"{OPENSEARCH_URL}/{opensearch_index}/_doc"
    response = requests.post(
        url, json=opensearch_document, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    if response.status_code != 201:
        raise Exception(f"Error indexing document! Cause: " + response.text)


def bulk_index_documents(
    opensearch_index: str, opensearch_documents: List[dict]
) -> int:
    """
    The optional JSON document doesn’t need to be minified—spaces are fine—but it does need to be on a single line.
    OpenSearch uses newline characters to parse bulk requests and requires that the request body end with a newline character.
    TODO: implement https://opensearch.org/docs/2.11/api-reference/document-apis/bulk/#path-and-http-methods
    """
    url = f"{OPENSEARCH_URL}/{opensearch_index}/_bulk"
    raise NotImplementedError


def find_documents(root_dir: str, file_pattern: str) -> list:
    document_paths = []
    for folder, _, _ in os.walk(root_dir):
        for file in glob.glob(os.path.join(folder, file_pattern)):
            document_paths.append(file)
    return document_paths


def process_document(document_path: str, root_dir: str, opensearch_index: str):
    document_title = document_path.replace("_", " ").split("/")[-1][:-4]
    document_uri = document_path[len(root_dir) :]

    pdf_loader = PyPDFium2Loader(document_path)
    pdf_pages = pdf_loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=64, length_function=len, is_separator_regex=False
    )
    chunks = text_splitter.split_documents(pdf_pages)

    print(f"Indexing {len(chunks)} chunks in OpenSearch ...")
    for chunk in chunks:
        opensearch_document = {
            "text": chunk.page_content,
            "metadata": {
                "document_title": document_title,
                "document_uri": document_uri,
                "document_page": chunk.metadata["page"],
            },
        }
        index_document(opensearch_index, opensearch_document)


def process_documents(document_paths: list, root_dir: str, opensearch_index: str):
    print(f"Processing {len(document_paths)} documents ...")
    for index, document_path in enumerate(document_paths):
        print(
            f"Processing document {index + 1} / {len(document_paths)} {document_path} ..."
        )
        process_document(document_path, root_dir, opensearch_index)


def main():
    global OPENSEARCH_URL, OPENSEARCH_CERT, OPENSEARCH_CA

    conf_file = resources.files("scripts.genai-openai-rag.resources").joinpath(
        "state.ini"
    )
    state = configparser.ConfigParser()
    state.read(str(conf_file))

    opensearch_use_ssl = bool(state["OS"]["ssl"]) or False
    if opensearch_use_ssl:
        cert_path = resources.files("scripts.genai-openai-rag.resources").joinpath(
            "client.pem"
        )
        key_path = resources.files("scripts.genai-openai-rag.resources").joinpath(
            "client.key"
        )
        ca_path = resources.files("scripts.genai-openai-rag.resources").joinpath(
            "ca.pem"
        )

        OPENSEARCH_CERT = (cert_path, key_path)
        OPENSEARCH_CA = ca_path

    OPENSEARCH_URL = state["OS"]["url"] or "http://127.0.0.1:9200"
    opensearch_index = state["index"]["index_name"] or "openai-rag"
    root_dir = str(
        resources.files("scripts.genai-openai-rag.resources").joinpath("docs")
    )
    file_pattern = "*.pdf"

    delete_all_documents(opensearch_index)
    document_paths = find_documents(root_dir, file_pattern)
    process_documents(document_paths, root_dir, opensearch_index)


if __name__ == "__main__":
    main()
