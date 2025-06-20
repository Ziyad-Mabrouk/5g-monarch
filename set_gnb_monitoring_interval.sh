#!/bin/bash

# Check if interval is provided as argument
if [[ -n "$1" ]]; then
  INTERVAL="$1"
else
  # Read from .env if no argument provided
  INTERVAL=$(grep '^MONARCH_MONITORING_INTERVAL=' .env | cut -d '=' -f2 | tr -d '"')
fi


if [[ "$INTERVAL" == *ms ]]; then
  MS=${INTERVAL%ms}
elif [[ "$INTERVAL" == *s ]]; then
  SECONDS=${INTERVAL%s}
  if ! [[ "$SECONDS" =~ ^[0-9]+$ ]]; then
    echo "Invalid interval format: $INTERVAL"
    exit 1
  fi
  MS=$((SECONDS * 1000))
else
  echo "Unsupported MONARCH_MONITORING_INTERVAL format: $INTERVAL"
  echo "   Supported formats: <int>ms or <int>s"
  exit 1
fi

POD=$(kubectl get pods -n open5gs -o name | grep oai-flexric | head -n1 | cut -d '/' -f2)

if [[ -z "$POD" ]]; then
  echo "Could not find oai-flexric pod in 'open5gs' namespace"
  exit 1
fi

echo "Setting gNB log interval to ${MS}ms using OAI-FlexRIC (pod: $POD)"
kubectl exec -n open5gs "$POD" -- bash -c "/usr/local/flexric/xApp/c/ctrl/xapp_mac_ctrl $MS"
