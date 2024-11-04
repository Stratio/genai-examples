### GenAI Chain Echo

This chain returns the input string.

### Chain Configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "chain_echo",
  "chain_config": {
    "package_id": "genai_chain_examples-0.1.0",
    "chain_module": "genai_chain_echo.chain",
    "chain_class": "EchoChain",
    "chain_params": {
      "response_delay": 0.0
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

* Any string

Example JSON:

```json
{
  "input": "hello world",
  "config": {},
  "kwargs": {}
}
```

### Invoke output

Example JSON:

```json
{
  "output": "Input was: hello world",
  "callback_events": [],
  "metadata": {
    "run_id": "4bb18fe0-de4f-49d7-82e6-72487a5fe6bd"
  }
}
```
