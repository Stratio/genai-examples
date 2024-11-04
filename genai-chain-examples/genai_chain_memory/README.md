### GenAI Chain Memory 

This chain calls the OpenAI Chat to generate answers about a topic with persisted memory.

Note that is neccesary to add lmdb as a project dependency to make use of wide Wide Column Chat Message History.

### Chain Configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "chain_mem",
  "chain_config": {
    "package_id": "genai_chain_examples-0.1.0",
    "chain_module": "genai_chain_memory.chain",
    "chain_class": "MemoryChain",
    "chain_params": {
      "openai_stratio_credential": "openai-token",
      "chat_temperature": 0.5
    },
    "worker_config": {
      "log_level": "info",
      "workers": 1
    }
  }
}
```

### Invoke
#### Input

* `topic`: Topic of the conversation.
* `input`: Message from human.

#### Config

* `session_id`: message chat history identification

Example JSON:

```json
{
  "input": {
    "topic": "cars",
    "input": "what was my first question?"
  },
  "config": {
    "configurable": {
      "session_id": "truco"
      }
  },
  "kwargs": {}
}
```

### Invoke Output

Example JSON:

```json
{
  "output": {
    "content": "Your first question was about the different types of car engines.",
    "additional_kwargs": {},
    "response_metadata": {
    "token_usage": {
      "completion_tokens": 12,
      "prompt_tokens": 38,
      "total_tokens": 50
    },
    "model_name": "gpt-3.5-turbo",
    "system_fingerprint": "fp_b28b39ffa8",
    "finish_reason": "stop",
    "logprobs": null
    },
  "type": "ai",
  "name": null,
  "id": "run-072d9831-d0ee-4057-b7e6-4ac2d1893413-0",
  "example": false,
  "tool_calls": [],
  "invalid_tool_calls": []
  },
  "callback_events": [],
  "metadata": {
    "run_id": "40d14507-2b25-483e-954b-87956ecd0d5f"
  }
}
```
