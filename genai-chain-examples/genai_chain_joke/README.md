### GenAI Chain Joke

This chain calls the OpenAI Chat to generate a joke.

### Chain Configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "chain_joke",
  "chain_config": {
    "package_id": "genai_chain_examples-0.3.0",
    "chain_module": "genai_chain_joke.chain",
    "chain_class": "JokeChain",
    "chain_params": {
      "openai_stratio_credential": "openai-token",
      "chat_temperature": 0.5
    },
    "worker_config": {
      "log_level": "info",
      "workers": 1,
      "invoke_timeout": 120
    }
  }
}
```

### Invoke input

* `topic`: Topic of the joke.

Example JSON:

```json
{
  "input": {
    "topic": "cars"
  },
  "config": {},
  "kwargs": {}
}
```

### Invoke output

Example JSON:

```json
{
  "output": {
    "content": "Why don't cars make good comedians? \n\nBecause their jokes always run out of gas!",
    "additional_kwargs": {},
    "type": "ai",
    "example": false
  },
  "callback_events": [],
  "metadata": {
    "run_id": "256e6683-09ef-4844-9a8d-d6fe64661807"
  }
}
```
