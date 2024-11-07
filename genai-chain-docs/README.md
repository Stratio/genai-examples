## GenAI Chain Docs

This repository contains a chain for RAG using OpenSearch as vector storage and OpenAI as chat model.

## Deployment

### Deploy in local

1. Execute `docker-compose up -d` to start the services.
2. Execute `scripts/load_vault_secrets.py` to load the secrets in Vault.
3. Run the Chain:
   * Execute `main.py` in PyCharm.
   * Or execute `poetry run start` or `python main.py` in a terminal.
   * Or load the chain in GenAI API server: http://127.0.0.1:8081

Services in docker-compose:

* GenAI API URL: http://127.0.0.1:8081
* Vault URL: http://127.0.0.1:8200
* Vault token: root-token
* OpenSearch Dashboards URL: http://127.0.0.1:5601
* OpenSearch URL: http://127.0.0.1:9200

To stop the services:

1. Execute `docker-compose down` to stop the services.
2. Execute `docker-compose down -v` to remove the persistent data.

### Run tests

Run in PyCharm:

* Execute the /tests folder. It works in debug mode too.

Run in the terminal:

* Execute `poetry run pytest`
* Only unit test: `poetry run pytest tests/unit`
* Only integration test: `poetry run pytest tests/integration`.

### Code quality

Run in the terminal:

* To format the code execute `poetry run black ./`
* To lint the code execute `poetry run pylint './**/'`
* To check the types execute `poetry run mypy ./`

### Configure the secrets in Vault

Configure the OpenAI token:

* Engine: userland
* Path: /passwords/genai-api.s000001-genai/openai-token
* Secret data:
  * token = `<openai-token>`

NOTE: To deploy in a Stratio environment you have to replace "genai-api.s000001-genai" in the path with the name of the service.

### Chain configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "chain_docs",
  "chain_config": {
    "package_id": "genai_chain_docs-0.3.0",
    "chain_module": "genai_chain_docs.chain",
    "chain_class": "DocsChain",
    "chain_params": {
      "opensearch_url": "http://opensearch:9200",
      "opensearch_index": "adif-rag",
      "opensearch_use_ssl": false,
      "openai_stratio_credential": "openai-token",
      "chat_temperature": 0.0
    },
    "worker_config": {
      "log_level": "info",
      "workers": 1,
      "invoke_timeout": 120
    }
  }
}
```

Chain configuration variables:
* opensearch_url: OpenSearch cluster URL. This URL usually includes the scheme (for example, "http" or "https"), the host name, and the port number.
* opensearch_index: Name of the index in the OpenSearch cluster where operations will be performed, such as indexing, retrieving, or searching data.
* opensearch_embedding_model_id (optional): Identification of the model obtained through the index. If not obtained, it must be specified in the configuration.
* opensearch_use_ssl (optional, default value = True): Indicates whether access is done securely through an SSL certificate.
* openai_stratio_credential (optional, default value = "openai-token"): Vault credentials to get openai key.
* chat_temperature (optional, default value = 0.0): Adjusts the variation and randomness of the output, generating "hallucinations" if a very high value is specified.
* show_references (optional, default value = True): Indicates whether the references of the documents used to obtain the response are displayed in the output.

NOTE: To deploy in a Stratio environment you have to replace the URL with the HTTPS URL of the OpenSearch service (eg: https://os-genai.s000001-genai:9200) and set "opensearch_use_ssl" to true.

### Invoke params

* `input`: Question to ask.

Example JSON:

```json
{
  "input": "que es el arco eléctrico?",
  "config": {},
  "kwargs": {}
}
```


## Architecture

A typical RAG application has two main components:
* **Indexing**: a pipeline for ingesting data from a source and indexing it. This usually happen offline.
  * **Load**: First we need to load our data. We'll use DocumentLoaders for this.
  * **Split**: Text splitters break large Documents into smaller chunks. This is useful both for indexing data and for passing it in to a model, since large chunks are harder to search over and won't in a model's finite context window.
  * **Store**: We need somewhere to store and index our splits, so that they can later be searched over. This is often done using a VectorStore and Embeddings model.
* **Retrieval and generation**: the actual RAG chain, which takes the user query at run time and retrieves the relevant data from the index, then passes that to the model.
  * **Retrieve**: Given a user input, relevant splits are retrieved from storage using a Retriever.
  * **Generate**: A ChatModel / LLM produces an answer using a prompt that includes the question and the retrieved data.

### Indexing

Indexing the documents in the vector storage is out of the scope of the GenAI Framework.
However, documents must be indexed in a specific format in order to be retrieved.

You can find the Python scripts used for a POC in the [scripts](./scripts) folder.

#### 1. Load

In this step you have to extract the content of the documents in plain text and the related metadata. You can use documents of any type, but you must make sure that the data is clean. You must be especially careful with formatted text, such as tables, and with indexes, headers and footers.

Example output:
```json
{
  "documents": [
    {
      "title": "Document title",
      "uri": "/files/document1.pdf",
      "content": [
        {
          "page": 1,
          "text": "Page text 1"
        }
      ]
    }
  ]
}
```

#### 2. Split

In this step you have to transform the documents into smaller chunks.

Example output:
```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Page text 1",
      "metadata": {
        "document_title": "Document title",
        "document_uri": "/files/document1.pdf",
        "document_page": 1
      }
    }
  ]
}
```

#### 3. Store

In this step you have to store the chunks in a vector storage. Before indexing the chunks, you have to calculate the embeddings using an embedding model.

Example output:
```json
{
  "chunks": [
    {
      "id": 1,
      "text": "Page text 1",
      "text_embedding": [-0.01072904, 0.03915191, -0.024826167, 0.113778464],
      "metadata": {
        "document_title": "Document title",
        "document_uri": "/files/document1.pdf",
        "document_page": 1
      }
    }
  ]
}
```

### Retrieval and generation

The retrieval and generation are achieved using the "GenAI Chain Docs" explained in the first section.

* Retrieve: The user provides a questions, it's converted to embeddings (using OpenSearch features), and we perform a KNN search in OpenSearch. OpenSearch will return the relevant chunks indexed in the previous sections.

* Generate: We build a "prompt" with the user question and the relevant documents. ChatGPT will redact the answer with information from the provided context.

### Useful commands for OpenSearch

```bash
# Check the configuration of an index
GET adif-rag

# See the documents indexed
GET adif-rag/_search
{
  "query": {
    "match_all": {}
  }
}

# Get the embeddings model ID
GET /_ingest/pipeline/adif-rag-ingest-pipeline

# Load model by Id
POST /_plugins/_ml/models/w_WH2YwBJct3ez1dVK2R/_load
GET /_plugins/_ml/tasks/QTvC7owBmF3TKd45JDPQ

# Check the ML models loaded
GET /_plugins/_ml/stats
```

### Steps to test opensearch with openai embeddings

1- Download ca.pem, clent.key, client.pem from stratio data fabric to genai-openai-rag/resources directory.
2- Configure genai-openai-rag/resources/state.init accordinf to you environment: OS.url and OS.ssl are the
two most important parameters.
3- run create_index script to initialise openai-rag index with openai-embedding connector.
https://github.com/opensearch-project/ml-commons/blob/2.x/docs/remote_inference_blueprints/openai_connector_embedding_blueprint.md#openai-connector-blueprint-example-for-embedding-model

``` bash
poetry run python scripts/genai-openai-rag/create_index.py
```
4- run process_documents script to index all pdf documetns stored in genai-openai-rag/resources/docs/ directory.

``` bash
poetry run python scripts/genai-openai-rag/process_documents.py
```

### Useful commands for OpenSearch with openai embedding

``` bash
# Generate openai embedding from text
POST /_plugins/_ml/models/openai-embedding/_predict
{
  "parameters": {
    "input": [ "Todas las fisuras en extremos embridados" ]
  }
}

# Search with openai embedding model
GET /openai-rag/_search
{
  "_source": {
    "excludes": [
      "text_embeddings"
    ]
  },
  "query": {
    "neural": {
      "text_embeddings": {
        "query_text": "procedimiento de reparación",
        "model_id": "openai-embedding",
        "k": 100
      }
    }
  }
}
```

### References

* https://python.langchain.com/docs/use_cases/question_answering/
