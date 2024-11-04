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


def upload_model(model: dict) -> str:
    print("Uploading model...")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/models/_upload"
    response = requests.post(
        url, json=model, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA
    )
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    task_info = wait_for_ml_task(task_id)
    model_id = task_info["model_id"]
    print(f"Model uploaded. Model ID: {model_id}")
    return model_id


def load_model(model_id: str) -> str:
    print(f"Loading model with ID {model_id} ...")
    url = f"{OPENSEARCH_URL}/_plugins/_ml/models/{model_id}/_load"
    response = requests.post(url, cert=OPENSEARCH_CERT, verify=OPENSEARCH_CA)
    assert response.status_code == 200
    task_id = response.json()["task_id"]
    task_info = wait_for_ml_task(task_id)
    model_id = task_info["model_id"]
    print(f"Model loaded. Model ID: {model_id}")
    return model_id


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
    assert response.status_code == 200
    print(f"Ingest pipeline created. Pipeline ID: {pipeline_id}")
    return pipeline_id


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
        "settings": {"index.knn": True, "default_pipeline": pipeline_id},
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
    print(f"Test query successful!")


def main():
    global OPENSEARCH_URL, OPENSEARCH_CERT, OPENSEARCH_CA

    opensearch_use_ssl = False
    if opensearch_use_ssl:
        cert_path = "/home/ddelasheras/Documentos/POC-ADIF-RAG/certs-yankee/client.crt"
        key_path = "/home/ddelasheras/Documentos/POC-ADIF-RAG/certs-yankee/client.key"
        ca_path = "/home/ddelasheras/Documentos/POC-ADIF-RAG/certs-yankee/ca.pem"

        OPENSEARCH_URL = "https://os-genai.s000001-genai:19200"
        OPENSEARCH_CERT = (cert_path, key_path)
        OPENSEARCH_CA = ca_path
    else:
        OPENSEARCH_URL = "http://127.0.0.1:9200"

    opensearch_index = "adif-rag"
    # https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/#supported-pretrained-models
    # model = {
    #     "name": "huggingface/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    #     "version": "1.0.1",
    #     "model_format": "TORCH_SCRIPT"
    # }
    # model_dimension = 384
    model = {
        "name": "multilingual-e5-large",
        "version": "1.0.0",
        "description": "Text Embeddings by Weakly-Supervised Contrastive Pre-training",
        "model_format": "ONNX",
        "model_config": {
            "model_type": "xlm-roberta",
            "embedding_dimension": 1024,
            "framework_type": "sentence_transformers",
            "all_config": """
{
    "_name_or_path": "intfloat/multilingual-e5-large",
    "architectures": [
        "XLMRobertaModel"
    ],
    "attention_probs_dropout_prob": 0.1,
    "bos_token_id": 0,
    "classifier_dropout": null,
    "eos_token_id": 2,
    "hidden_act": "gelu",
    "hidden_dropout_prob": 0.1,
    "hidden_size": 1024,
    "initializer_range": 0.02,
    "intermediate_size": 4096,
    "layer_norm_eps": 0.00001,
    "max_position_embeddings": 514,
    "model_type": "xlm-roberta",
    "num_attention_heads": 16,
    "num_hidden_layers": 24,
    "output_past": true,
    "pad_token_id": 1,
    "position_embedding_type": "absolute",
    "transformers_version": "4.30.2",
    "type_vocab_size": 1,
    "use_cache": true,
    "vocab_size": 250002
}
""",
        },
        "url": "http://qa.int.stratio.com/repository/raw/genai-models/multilingual-e5-large.zip",
    }
    model_dimension = 1024
    pipeline_id = opensearch_index + "-ingest-pipeline"
    model_id = upload_model(model)
    load_model(model_id)
    create_ingest_pipeline(model_id, pipeline_id)
    delete_index(opensearch_index)
    create_index(opensearch_index, pipeline_id, model_dimension)
    perform_test_search(opensearch_index, model_id)


if __name__ == "__main__":
    main()
