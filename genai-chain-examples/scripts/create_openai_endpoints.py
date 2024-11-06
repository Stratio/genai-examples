"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import os

import httpx
from genai_core.constants.constants import ENV_VAR_GENAI_GATEWAY_URL


def get_genai_gateway_base_url() -> str:
    return os.environ.get(ENV_VAR_GENAI_GATEWAY_URL, "http://127.0.0.1:8082")


def create_openai_chat_point() -> None:
    url = f"{get_genai_gateway_base_url()}/v1/endpoints"
    payload = {
        "id": "openai-chat-gpt-4o-mini",
        "endpoint_type": "llm/v2/chat",
        "model": {
            "name": "gpt-4o-mini-2024-07-18",
            "provider": "openai",
            "input_cost_1k_tokens": 0.00015,
            "output_cost_1k_tokens": 0.0006,
            "token_limit": 128000,
            "config": {
                "stratio_credential": "openai-token",
                "openai_api_type": "openai",
                "openai_api_base": "https://api.openai.com/v1",
            },
        },
    }
    response = httpx.post(url, json=payload)
    if response.status_code != 201:
        raise Exception(
            "Error creating OpenAI Chat endpoint. "
            f"HTTP Code: {response.status_code} Cause: {response.text}"
        )


def create_openai_completions_point() -> None:
    url = f"{get_genai_gateway_base_url()}/v1/endpoints"
    payload = {
        "id": "openai-completions-gpt-4o",
        "endpoint_type": "llm/v1/completions",
        "model": {
            "name": "gpt-4o",
            "provider": "openai",
            "config": {
                "stratio_credential": "openai-token",
                "openai_api_type": "openai",
                "openai_api_base": "https://api.openai.com/v1",
            },
        },
    }
    response = httpx.post(url, json=payload)
    if response.status_code != 201:
        raise Exception(
            "Error creating OpenAI Completions endpoint. "
            f"HTTP Code: {response.status_code} Cause: {response.text}"
        )


def create_openai_embeddings_point() -> None:
    url = f"{get_genai_gateway_base_url()}/v1/endpoints"
    payload = {
        "id": "openai-embeddings-text-embedding-ada-002",
        "endpoint_type": "llm/v1/embeddings",
        "model": {
            "name": "text-embedding-ada-002",
            "provider": "openai",
            "config": {
                "stratio_credential": "openai-token",
                "openai_api_type": "openai",
                "openai_api_base": "https://api.openai.com/v1",
            },
        },
    }
    response = httpx.post(url, json=payload)
    if response.status_code != 201:
        raise Exception(
            "Error creating OpenAI Embeddings endpoint. "
            f"HTTP Code: {response.status_code} Cause: {response.text}"
        )


def main() -> None:
    create_openai_chat_point()
    create_openai_completions_point()
    create_openai_embeddings_point()
    print("Endpoints created!")


if __name__ == "__main__":
    """
    Usage:
    - Execute `scripts/load_vault_secrets.py` to load the secrets in Vault before running this script.
    """
    main()
