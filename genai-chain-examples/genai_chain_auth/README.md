### GenAI Chain Auth

Return the authorization information.

### Chain Configuration

Example configuration for [GenAI API](https://github.com/Stratio/genai-api):

```json
{
  "chain_id": "chain_auth",
  "chain_config": {
    "package_id": "genai_chain_examples-0.1.0",
    "chain_module": "genai_chain_auth.chain",
    "chain_class": "AuthChain",
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
    "input": "Example input",
    "auth": {
      "auth_type": "sso",
      "cn": "admin",
      "email": "admin@fifteen.int",
      "expiration": 1706151981,
      "tenant": "s000001",
      "uid": "admin"
    },
    "is_auth": true
  },
  "callback_events": [],
  "metadata": {
    "run_id": "eb95b6db-3082-40c2-9f42-670f90cddc7e"
  }
}
```
