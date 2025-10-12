#!/bin/bash
kubectl get pods -n monarch -l app=monarch,component=kpi-calculator-open5gs -o json | jq .items[].metadata.name