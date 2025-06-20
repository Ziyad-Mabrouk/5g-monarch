#!/bin/bash

INTERVAL=$(grep '^MONARCH_MONITORING_INTERVAL=' .env | cut -d '=' -f2 | tr -d '"')

if [[ "$INTERVAL" == *ms ]]; then
  MS=${INTERVAL%ms}
elif [[ "$INTERVAL" == *s ]]; then
  MS=$(( ${INTERVAL%s} * 1000 ))
else
  echo "Unsupported MONARCH_MONITORING_INTERVAL format: $INTERVAL"
  exit 1
fi

# Find the oai-flexric pod
POD=$(kubectl get pods -n open5gs -o name | grep oai-flexric | head -n1 | cut -d '/' -f2)

if [[ -z "$POD" ]]; then
  echo "Could not find oai-flexric pod in 'monarch' namespace"
  exit 1
fi

# Execute xapp_mac_ctrl with the parsed interval
echo "Setting gNB log interval to ${MS}ms using OAI-FlexRIC"
kubectl exec -n open5gs "$POD" -- bash -c "/usr/local/flexric/xApp/c/ctrl/xapp_mac_ctrl $MS"
