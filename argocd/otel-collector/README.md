# OpenTelemetry Collector Helm Chart

This folder contains the `values.yaml` for deploying the OpenTelemetry Collector as a DaemonSet to collect both application and host metrics.

- Uses the `otel/opentelemetry-collector-contrib` image.
- Collects application telemetry via OTLP (gRPC/HTTP).
- Collects host metrics (CPU, memory, disk, filesystem, network) from each node.
- Exports all telemetry to the collector's logs by default (for testing/demo purposes).

## Install

```sh
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update
helm install otel-collector open-telemetry/opentelemetry-collector \
  --namespace observability \
  --create-namespace \
  -f ./values.yaml
```

## Customization
- To export telemetry to a central collector or another backend, edit the `exporters` section in `values.yaml`. 