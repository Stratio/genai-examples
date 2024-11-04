#!/usr/bin/env bash
KUBE_CONFIG="$HOME/.kube/fifteen_config"

while true
do
  echo "Starting OpenSearch tunnel..."
  kubectl --kubeconfig "$KUBE_CONFIG" port-forward services/os-genai-coordinator 19200:9200 -n s000001-datastores &
  wait
  echo "Restarting OpenSearch tunnel in 5 seconds..."
  sleep 5
done
