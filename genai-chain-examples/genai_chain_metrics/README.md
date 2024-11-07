### GenAI Chain Metrics

Publish a custom Prometheus metric from the GenAI chain.

### Chain Configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "chain_metrics",
  "chain_config": {
    "package_id": "genai_chain_examples-0.3.0",
    "chain_module": "genai_chain_metrics.chain",
    "chain_class": "MetricsChain",
    "chain_params": {},
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
  "input": "Example input",
  "config": {},
  "kwargs": {}
}
```

### Invoke output

Example JSON:

```json
{
  "output": {
    "input": "Example input"
  },
  "callback_events": [],
  "metadata": {
    "run_id": "eb95b6db-3082-40c2-9f42-670f90cddc7e"
  }
}
```

### Prometheus metrics

```text
# HELP genai_chain_invoke_counter Number of requests to the invoke method.
# TYPE genai_chain_invoke_counter gauge
genai_chain_invoke_counter{chain_id="example_chain",label1="value1"} 1.0
```
