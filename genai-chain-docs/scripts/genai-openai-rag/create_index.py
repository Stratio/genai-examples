"""
© 2024 Stratio Big Data Inc., Sucursal en España. All rights reserved.

This software – including all its source code – contains proprietary
information of Stratio Big Data Inc., Sucursal en España and
may not be revealed, sold, transferred, modified, distributed or
otherwise made available, licensed or sublicensed to third parties;
nor reverse engineered, disassembled or decompiled, without express
written authorization from Stratio Big Data Inc., Sucursal en España.
"""
import time
from os import environ
from importlib import resources
import configparser
import requests

OPENSEARCH_URL = ""
OPENSEARCH_CERT = ""
OPENSEARCH_CA = ""


def wait_for_ml_task(task_id: str) -> dict:
    print(f"Waiting for ML task {task_id} ...")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/tasks/{task_id}"
    task_info = {}
    task_state = "CREATED"
    while task_state != "COMPLETED" and task_state != "FAILED":
        time.sleep(5)
        response = requests.get(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
        assert response.status_code == 200
        task_info = response.json()
        task_state = task_info["state"]
        print(f"Task state: {task_state}")
    if task_state != "COMPLETED":
        raise Exception(f"Task {task_id} failed! Cause: " + task_info["error"])
    return task_info


def add_trusted_endpoints() -> None:
    print(f"Allow external LLM uris...")
    config = {
        "persistent": {
            "plugins.ml_commons.trusted_connector_endpoints_regex": [
                "^https://runtime\\.sagemaker\\..*[a-z0-9-]\\.amazonaws\\.com/.*$",
                "^https://api\\.openai\\.com/.*$",
                "^https://api\\.cohere\\.ai/.*$",
                "^https://bedrock-runtime\\..*[a-z0-9-]\\.amazonaws\\.com/.*$",
            ]
        }
    }
    url = f"{OPENSEARCH_URL}/_cluster/settings"
    response = requests.put(
        url, json=config, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200


def register_model_group(name: str, description=None) -> str:
    model_group = {
        "name": name.replace(" ", "_"),
        "description": "A model group for external models",
    }
    url = f"{OPENSEARCH_URL}/_plugins/_ml/model_groups/_register"
    response = requests.post(
        url, json=model_group, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    try:
        assert response.status_code == 200
        if response.json()["status"] != "CREATED":
            raise ValueError(f"Model group {name} was not created")

        return response.json()["model_group_id"]
    except Exception as err:
        print(f"failes registering model group:: {err}")
        raise ValueError(err)


def creating_embedding_connector() -> str:
    print("Creating embedding connector...")
    connector = {
        "name": "openai-embedding",
        "description": "connector to generate embeddings",
        "version": "1",
        "protocol": "http",
        "parameters": {"model": "text-embedding-ada-002"},
        "credential": {"openAI_key": "<PLEASE ADD YOUR OPENAI API KEY HERE>"},
        "actions": [
            {
                "action_type": "predict",
                "method": "POST",
                "url": "https://api.openai.com/v1/embeddings",
                "headers": {"Authorization": "Bearer ${credential.openAI_key}"},
                "request_body": '{ "input": ${parameters.input}, "model": "${parameters.model}" }',
                "pre_process_function": "connector.pre_process.openai.embedding",
                "post_process_function": "connector.post_process.openai.embedding",
            }
        ],
    }
    connector["credential"]["openAI_key"] = environ.get("OPENAI_TOKEN")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/connectors/_create"
    response = requests.post(
        url, json=connector, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200
    connector_id = response.json()["connector_id"]
    print(f"configured connector with ID: {connector_id}")
    return connector_id


def register_model(model_group_id: str, connector_id: str) -> str:
    model = {
        "name": "openai-embedding",
        "function_name": "remote",
        "model_group_id": model_group_id,
        "description": "embedding model",
        "connector_id": connector_id,
    }
    print(
        f"Registering externally hosted model with group ID {model_group_id} and connector_id {connector_id}..."
    )
    url = f"{OPENSEARCH_URL}/_plugins/_ml/models/_register"
    response = requests.post(
        url, json=model, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    task_info = wait_for_ml_task(task_id)
    model_id = task_info["model_id"]
    print(f"Model loaded. Model ID: {model_id}")
    return model_id


def deploy_model(model_id: str, assert_model: bool = True) -> None:
    url = f"{OPENSEARCH_URL}/_plugins/_ml/models/{model_id}/_deploy"
    response = requests.post(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    task_info = wait_for_ml_task(task_id)
    model_id = task_info["model_id"]
    print(f"Model deployed. Model ID: {model_id}")

    if assert_model:
        url = f"{OPENSEARCH_URL}/_plugins/_ml/models/{model_id}/_predict"
        doc = {"parameters": {"input": ["What is the meaning of life?"]}}
        response = requests.post(
            url, json=doc, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
        )
        assert response.status_code == 200
        # https://github.com/opensearch-project/ml-commons/blob/2.x/docs/remote_inference_blueprints/openai_connector_embedding_blueprint.md#4-test-model-inference
        assert len(response.json()["inference_results"][0]["output"][0]["data"]) > 0


def create_ingest_pipeline(model_id: str, pipeline_id: str) -> str:
    print(f"Creating ingest pipeline with ID {pipeline_id} ...")
    url = f"{OPENSEARCH_URL}/_ingest/pipeline/{pipeline_id}"
    pipeline = {
        "description": "Ingest pipeline to generate text embeddings",
        "processors": [
            {
                "text_embedding": {
                    "model_id": model_id,
                    "field_map": {"text": "text_embeddings"},
                }
            }
        ],
    }
    response = requests.put(
        url, json=pipeline, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    try:
        assert response.status_code == 200
        print(f"Ingest pipeline created. Pipeline ID: {pipeline_id}")
        return pipeline_id
    except Exception as err:
        print(
            f"Ingest pipeline err: code: {response.status_code}, err: {response.json()}"
        )


def delete_index(opensearch_index: str):
    print(f"Deleting index with ID {opensearch_index} ...")
    url = f"{OPENSEARCH_URL}/{opensearch_index}"
    response = requests.delete(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code == 200 or response.status_code == 404
    print(f"Index deleted. Index ID: {opensearch_index}")


def create_index(opensearch_index: str, pipeline_id: str, model_dimension: int) -> str:
    print(f"Creating index with ID {opensearch_index} ...")
    url = f"{OPENSEARCH_URL}/{opensearch_index}"
    index_config = {
        "settings": {"index.knn": True, "default_pipeline": f"{pipeline_id}"},
        "mappings": {
            "properties": {
                "text": {"type": "text", "index": False},
                "text_embeddings": {
                    "type": "knn_vector",
                    "dimension": model_dimension,
                    "method": {
                        "engine": "nmslib",
                        "space_type": "cosinesimil",
                        "name": "hnsw",
                        "parameters": {"ef_construction": 712, "m": 16},
                    },
                },
            },
            "dynamic_templates": [
                {"metadata": {"match": "*", "mapping": {"index": False}}}
            ],
        },
    }
    response = requests.put(
        url, json=index_config, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200
    print(f"Index created. Index ID: {opensearch_index}")
    return opensearch_index


def perform_test_search(opensearch_index: str, model_id: str):
    print(f"Testing search with index {opensearch_index} ...")
    url = f"{OPENSEARCH_URL}/{opensearch_index}/_search"
    query = {
        "_source": {"excludes": ["text_embeddings"]},
        "query": {
            "neural": {
                "text_embeddings": {"query_text": "test", "model_id": model_id, "k": 3}
            }
        },
    }
    response = requests.post(
        url, json=query, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200
    print(f"Test query successful! {response.json()}")


def clean(state):
    print(f"unregister model {state['model']['model_id']}")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/models/{state['model']['model_id']}/_undeploy"
    response = requests.post(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code in (200, 404)
    print(f"remove model {state['model']['model_id']}")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/models/{state['model']['model_id']}"
    response = requests.delete(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code in (200, 404)
    print(f"remove connector {state['model']['connector_id']}")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/connectors/{state['model']['connector_id']}"
    response = requests.delete(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code in (200, 404)
    print(f"remove model group {state['model']['model_group_name']}")
    url = (
        f"{OPENSEARCH_URL}/_plugins/_ml/model_groups/{state['model']['model_group_id']}"
    )
    response = requests.delete(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code in (200, 404)

    delete_index(state["index"]["index_name"])
    print(
        f"remove ingest pipeline {state['index']['index_name']}{state['index']['pipeline_suffix']}"
    )
    url = f"{OPENSEARCH_URL}/_ingest/pipeline/{state['index']['index_name']}{state['index']['pipeline_suffix']}"
    response = requests.delete(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code in (200, 404)


def main():
    # https://opensearch.org/docs/latest/ml-commons-plugin/remote-models/connectors/#creating-a-standalone-connector
    # https://opensearch.org/docs/latest/ml-commons-plugin/remote-models/connectors/#supported-connectors``
    global OPENSEARCH_URL, OPENSEARCH_CERT, OPENSEARCH_CA

    conf_file = resources.files("scripts.genai-openai-rag.resources").joinpath(
        "state.ini"
    )
    state = configparser.ConfigParser()
    state.read(str(conf_file))

    opensearch_use_ssl = bool(state["OS"]["ssl"]) or False
    opensearch_use_ssl = True
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
    model_dimension = int(state["model"]["model_dimension"]) or 1536
    model_group_name = state["model"]["model_group_name"] or "embeddings-openai"

    clean_os = bool(state["OS"]["clean_on_startup"]) or False
    if clean_os:
        clean(state)

    add_trusted_endpoints()
    model_group_id = register_model_group(model_group_name)
    connector_id = creating_embedding_connector()
    model_id = register_model(model_group_id, connector_id)
    deploy_model(model_id)

    pipeline_id = opensearch_index + "-ingest-pipeline"
    create_ingest_pipeline(model_id, pipeline_id)
    delete_index(opensearch_index)
    create_index(opensearch_index, pipeline_id, model_dimension)
    perform_test_search(opensearch_index, model_id)

    state = configparser.ConfigParser()
    state["model"] = {}
    state["model"]["model_dimension"] = str(model_dimension)
    state["model"]["model_group_name"] = model_group_name
    state["model"]["model_group_id"] = model_group_id
    state["model"]["model_id"] = model_id
    state["model"]["connector_id"] = connector_id

    state["index"] = {
        "index_name": opensearch_index,
        "pipeline_name": opensearch_index + "-ingest-pipeline",
        "pipeline_id": pipeline_id,
        "pipeline_suffix": "-ingest-pipeline",
    }

    state["OS"] = {
        "url": OPENSEARCH_URL,
        "ssl": str(opensearch_use_ssl),
        "clean_on_startup": str(clean_os),
    }

    with open(str(conf_file), "w") as state_file:
        state.write(state_file)


if __name__ == "__main__":
    main()
