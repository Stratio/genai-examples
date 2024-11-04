#!/usr/bin/env bash
set -e

cd ~
KUBE_CONFIG=".kube/config_fifteen"

tunnelGateway() {
  while true
  do
    echo "Starting Gateway tunnel..."
    gateway_pod=$(kubectl --kubeconfig "$KUBE_CONFIG" get pods -n s000001-genai | grep genai-gateway- | awk '{ print $1 }')
    kubectl --kubeconfig "$KUBE_CONFIG" port-forward pods/${gateway_pod} 60001:8080 -n s000001-genai &
    wait
    echo "Restarting Gateway tunnel in 5 seconds..."
    sleep 5
  done
}


tunnelGateway &


wait
