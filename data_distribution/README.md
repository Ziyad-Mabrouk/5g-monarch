# thanos
Thanos deployment

# install
Use the [bitnamilegacy/thanos helm chart](https://artifacthub.io/packages/helm/bitnamilegacy/thanos)

```
helm install thanos -n thanos -f thanos-values.yaml bitnamilegacy/thanos
```

# enabling thanos components in prometheus helm chart

Remember to create the `thanos-objstore-config` secret first.

```yaml
thanos:
    image: quay.io/thanos/thanos:v0.31.0
    objectStorageConfig:
        key: thanos.yaml
        name: thanos-objstore-config
    
prometheus:
    thanosServiceExternal:
        enabled: true
        type: NodePort
```

