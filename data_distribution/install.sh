#!/bin/bash
THANOS_VER="12.4.3"
HELM_REPO_URL="oci://registry-1.docker.io/bitnamicharts"
NAMESPACE="monarch"
MODULE_NAME="datadist"

set -o allexport; source ../.env; set +o allexport

kubectl get namespace $NAMESPACE 2>/dev/null || kubectl create namespace $NAMESPACE

envsubst < thanos-values.yaml | helm upgrade --install $MODULE_NAME $HELM_REPO_URL/thanos \
        --namespace $NAMESPACE \
        --version $THANOS_VER \
        -f -