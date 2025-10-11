#!/bin/bash
THANOS_VER="12.4.3"
HELM_REPO_URL="oci://registry-1.docker.io/bitnamicharts"
NAMESPACE="monarch"
MODULE_NAME="datadist"

set -o allexport; source ../.env; set +o allexport

helm pull $HELM_REPO_URL/thanos --version $THANOS_VER
tar -xvf thanos-$THANOS_VER.tgz
cd thanos
grep -rl 'bitnami/' . | xargs sed -i 's|bitnami/|bitnamilegacy/|g'
cd ..

kubectl get namespace $NAMESPACE 2>/dev/null || kubectl create namespace $NAMESPACE

envsubst < thanos-values.yaml | helm upgrade --install $MODULE_NAME thanos \
        --namespace $NAMESPACE \
        --version $THANOS_VER \
        -f -