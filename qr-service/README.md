# QR Code Service

A high-performance QR code encoding and decoding service built with Python FastAPI, designed for cloud deployment on Kubernetes.

## Team Information
- **Team Name**: Cumulonimbus
- **AWS Account ID**: 587764054854

## Overview

This service implements a simplified QR code algorithm with the following features:
- **Encoding**: Convert plain text messages to QR code hex strings
- **Decoding**: Extract messages from QR codes and authenticate via REST API
- **Authentication**: Integration with authentication service for token generation
- **High Performance**: Optimized for throughput testing on cloud infrastructure

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Load Generator │────────▶│   QR Service     │
│    (Sail)       │         │   (FastAPI)      │
└─────────────────┘         └────────┬─────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Auth Service   │
                            │   (REST API)    │
                            └─────────────────┘
```

## QR Code Algorithm

### Version Selection
- **Version 1** (21×21): Messages with ≤13 characters
- **Version 2** (25×25): Messages with 14-22 characters

### Encoding Process
1. Generate payload: `[length][char1][EC1][char2][EC2]...`
2. Create QR matrix with structural patterns:
   - Position detection patterns (3 corners)
   - Timing patterns (row 6, column 6)
   - Alignment pattern (version 2 only)
3. Fill payload using zigzag pattern
4. Apply logistic map encryption (`x[n+1] = 4*x[n]*(1-x[n])`)
5. Convert to hex string

### Decoding Process
1. Parse hex string to 32×32 matrix
2. Locate QR code (detect position patterns)
3. Determine rotation (0°, 90°, 180°, 270°)
4. Reverse logistic map encryption
5. Extract payload via reverse zigzag
6. Authenticate with auth service
7. Return encrypted token

## Project Structure

```
qr-service/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application
│   ├── qr_encoder.py         # QR encoding logic
│   ├── qr_decoder.py         # QR decoding logic
│   ├── auth_client.py        # REST authentication client
│   └── utils.py              # Utility functions
├── helm/
│   ├── Chart.yaml            # Helm chart metadata
│   ├── values.yaml           # Configuration values
│   └── templates/
│       ├── deployment.yaml   # QR service deployment
│       ├── service.yaml      # QR service service
│       ├── auth-deployment.yaml  # Auth service deployment
│       ├── auth-service.yaml     # Auth service service
│       ├── hpa.yaml          # Horizontal Pod Autoscaler
│       └── ingress.yaml      # Ingress (optional)
├── Dockerfile                # Container image definition
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## API Endpoints

### Encoding
```
GET /qrcode?type=encode&data=<message>

Response:
Cumulonimbus,587764054854
0x66d92b800x5bc76d83...
```

### Decoding
```
GET /qrcode?type=decode&data=<hex_string>&timestamp=<unix_timestamp>

Response:
Cumulonimbus,587764054854
e6979c24e590d4b8bd1e30f3ab2751193467c030acaa3262d2125d884671eda9
```

### Health Check
```
GET /health

Response:
{"status": "healthy"}
```

## Local Development

### Prerequisites
- Python 3.11+
- Docker
- Kubernetes cluster (for deployment)
- Helm 3

### Run Locally

1. **Install dependencies**:
```bash
cd qr-service
pip install -r requirements.txt
```

2. **Run the service**:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

3. **Test encoding**:
```bash
curl "http://localhost:8080/qrcode?type=encode&data=Hello"
```

## Docker Build & Push

### Build Image
```bash
cd qr-service
docker build -t qr-service:latest .
```

### Tag for ECR
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 587764054854.dkr.ecr.us-east-1.amazonaws.com

# Create repository (first time only)
aws ecr create-repository --repository-name qr-service --region us-east-1

# Tag image
docker tag qr-service:latest 587764054854.dkr.ecr.us-east-1.amazonaws.com/qr-service:latest

# Push to ECR
docker push 587764054854.dkr.ecr.us-east-1.amazonaws.com/qr-service:latest
```

## Kubernetes Deployment

### Prerequisites
- EKS cluster provisioned
- kubectl configured
- Helm 3 installed

### Deploy with Helm

1. **Install the chart**:
```bash
cd qr-service
helm install qr-code-service ./helm
```

2. **Check deployment status**:
```bash
kubectl get pods
kubectl get services
```

3. **Get service URL**:
```bash
kubectl get service qr-service
# Note the EXTERNAL-IP for Load Balancer
```

### Configuration Options

Edit `helm/values.yaml` to customize:

- **Replica count**: Adjust `qrService.replicaCount`
- **Instance resources**: Modify `qrService.resources`
- **Autoscaling**: Configure `qrService.autoscaling`
- **Architecture**: Change `authService.image.tag` to `arm64` for ARM instances
- **Load balancer**: Change `qrService.service.type` to `NodePort` or use Ingress

### Update Deployment
```bash
# After changing values.yaml or pushing new image
helm upgrade qr-code-service ./helm
```

### Uninstall
```bash
helm uninstall qr-code-service
```

## Performance Optimization

### Framework Comparison
This implementation uses **FastAPI**. For comparison testing, consider:
- **Flask** with gunicorn
- **Go** with Gin or Fiber
- **Node.js** with Express or Fastify

### Kubernetes Optimization
- **Instance Types**: Test with different EC2 instance types (t3, c5, m5)
- **Cluster Size**: Vary number of nodes (3, 5, 10)
- **Replicas**: Adjust pod count (3-20)
- **Resources**: Tune CPU/memory limits
- **HPA**: Configure autoscaling thresholds

### Load Balancer Alternatives
- AWS Application Load Balancer (ALB)
- AWS Network Load Balancer (NLB)
- NGINX Ingress Controller
- Traefik

## Testing

### Unit Tests
```bash
# TODO: Add pytest tests
pytest tests/
```

### Load Testing
Use the Sail() load generator to test throughput:
- Target: 600-second submission reaching target throughput
- Monitor: Pod CPU/memory, request latency, error rate

### Manual Testing
```bash
# Encode test
curl "http://<LOAD_BALANCER_IP>/qrcode?type=encode&data=CC%20Team"

# Decode test (requires auth service running)
curl "http://<LOAD_BALANCER_IP>/qrcode?type=decode&data=0x66ede853...&timestamp=1706567290739"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEAM_NAME` | Cumulonimbus | Team name for responses |
| `TEAM_AWS_ID` | 587764054854 | AWS account ID |
| `AUTH_SERVICE_URL` | http://auth-service:9000 | Auth service endpoint |
| `PORT` | 8080 | Service port |

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Authentication failing
- Verify auth service is running: `kubectl get pods -l app=auth-service`
- Check auth service logs: `kubectl logs -l app=auth-service`
- Verify service DNS: `kubectl exec -it <qr-pod> -- nslookup auth-service`

### Performance issues
- Check HPA status: `kubectl get hpa`
- Monitor metrics: `kubectl top pods`
- Review resource limits in values.yaml

## License

Cloud Computing Course Project - CMU

## Authors

Team Cumulonimbus
