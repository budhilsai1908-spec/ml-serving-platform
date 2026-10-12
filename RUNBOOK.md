# Runbook — ML Serving Platform

Operational guide for running, deploying, scaling, and monitoring the platform locally.

---

## Prerequisites

- Docker Desktop
- kubectl
- kind
- helm
- Python 3.12

---

## 1. First-Time Setup

```bash
# Clone and enter the project
git clone https://github.com/budhilsai1908-spec/ml-serving-platform.git
cd ml-serving-platform

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train the model
python app/train.py

# Build the Docker image
docker build -t sentiment-api:v2 .

# Create the Kubernetes cluster
kind create cluster --name ml-platform

# Load the image into the cluster
kind load docker-image sentiment-api:v2 --name ml-platform

# Deploy with Helm
helm install sentiment ./sentiment-chart --set image.tag=v2
```

---

## 2. Install Monitoring (one-time)

```bash
# Metrics server (required for autoscaling)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# Prometheus + Grafana stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# ServiceMonitor so Prometheus scrapes the app
kubectl apply -f k8s/servicemonitor.yaml
```

---

## 3. Daily Restart (after rebooting your Mac)

The cluster, Helm releases, and monitoring stack persist across reboots.
Only Docker and the port-forwards need restarting.

```bash
# 1. Start Docker Desktop, then wait until it is running
open -a Docker

# 2. Confirm the cluster is back (wait until the node is Ready)
kubectl get nodes

# 3. Confirm your pods are running
kubectl get pods

# 4. Re-open the app tunnel (runs in background)
kubectl port-forward service/sentiment-api 8080:80 > /dev/null 2>&1 &

# 5. Re-open Grafana (runs in background)
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 > /dev/null 2>&1 &
```

---

## 4. Common Operations

### Test the API
```bash
curl http://localhost:8080/healthz
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "this is great"}'
```

### Deploy a new version
```bash
docker build -t sentiment-api:v3 .
kind load docker-image sentiment-api:v3 --name ml-platform
helm upgrade sentiment ./sentiment-chart --set image.tag=v3
```

### Roll back a bad deploy
```bash
helm history sentiment          # list revisions
helm rollback sentiment <REV>   # revert to a previous revision
```

### Scale demo (watch the autoscaler)
```bash
# In one terminal, watch the HPA
kubectl get hpa -w

# In another, generate load
for i in $(seq 1 2000); do
  curl -s -X POST http://localhost:8080/predict \
    -H "Content-Type: application/json" \
    -d '{"text": "load test"}' > /dev/null
done
```

### Access Grafana
```bash
# Get the admin password
kubectl --namespace monitoring get secrets monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d ; echo

# Open Grafana (after the port-forward from step 3.5 is running)
open http://localhost:3000
# Login: admin / <password from above>
```

---

## 5. Teardown

```bash
# Remove everything by deleting the cluster
kind delete cluster --name ml-platform
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `curl` connection refused | Port-forward died — re-run step 3.4 |
| Grafana won't load | Re-run step 3.5 |
| HPA shows `<unknown>` for CPU | metrics-server not ready — `kubectl get pods -n kube-system` |
| Pods stuck `ContainerCreating` | Image not loaded — re-run `kind load docker-image` |
| `uvicorn` NumPy error (local) | Use `python -m uvicorn` inside the venv, not bare `uvicorn` |
