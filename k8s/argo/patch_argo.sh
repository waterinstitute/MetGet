#!/bin/bash
kubectl patch deployment \
  argo-server \
  --namespace metget \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/args", "value": ["server","--auth-mode=server"]}]'
