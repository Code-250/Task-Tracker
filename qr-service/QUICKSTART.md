# QR Code Service - Quick Start Guide

Get your QR Code Service running in 5 minutes!

## Prerequisites

- Docker installed
- AWS CLI configured
- kubectl configured with EKS cluster access
- Helm 3 installed

## 🚀 Quick Deployment (5 Steps)

### 1. Build & Push to ECR

```bash
cd qr-service

# Run automated build and push script
./build-and-push.sh

# Or manually:
# docker build -t qr-service:latest .
# ... (see build-and-push.sh for full commands)
```

### 2. Verify Image in ECR

```bash
aws ecr describe-images \
  --repository-name qr-service \
  --region us-east-1
```

### 3. Deploy to Kubernetes

```bash
# Deploy everything (QR service + Auth service)
helm install qr-code-service ./helm

# Watch deployment
kubectl get pods -w
```

### 4. Get Service Endpoint

```bash
# Get Load Balancer URL
kubectl get service qr-service

# Wait for EXTERNAL-IP/HOSTNAME to be assigned
# (can take 2-3 minutes for AWS ELB provisioning)
```

### 5. Test the Service

```bash
# Set the endpoint
ENDPOINT=$(kubectl get service qr-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test encoding
curl "http://${ENDPOINT}/qrcode?type=encode&data=Hello"

# Should return:
# Cumulonimbus,587764054854
# 0x...hex...string...
```

## 🧪 Local Testing (Before Deployment)

### Test Python Code

```bash
cd qr-service

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_qr.py

# Should see:
# ✓ Version selection tests completed
# ✓ Encoder tests completed
# ✓ Round-trip tests completed
```

### Test Locally with Uvicorn

```bash
# Run the service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# In another terminal, test:
curl "http://localhost:8080/qrcode?type=encode&data=Test"
```

### Test with Docker

```bash
# Build image
docker build -t qr-service:test .

# Run container
docker run -p 8080:8080 \
  -e TEAM_NAME=Cumulonimbus \
  -e TEAM_AWS_ID=587764054854 \
  qr-service:test

# Test in another terminal
curl "http://localhost:8080/qrcode?type=encode&data=Test"
```

## 📊 Performance Testing Checklist

### Before Load Testing

- [ ] Service deployed and healthy: `kubectl get pods`
- [ ] HPA configured: `kubectl get hpa`
- [ ] Metrics server installed: `kubectl top pods`
- [ ] Load balancer endpoint accessible

### During Load Testing

Monitor in separate terminals:

```bash
# Terminal 1: Watch pods autoscale
kubectl get pods -l app=qr-service -w

# Terminal 2: Watch HPA
kubectl get hpa -w

# Terminal 3: Monitor resources
watch kubectl top pods

# Terminal 4: View logs
kubectl logs -f -l app=qr-service
```

### Required for Full Score

- [ ] 600-second submission on Sail()
- [ ] Reaches target throughput
- [ ] At least 2 framework implementations tested
- [ ] Kubernetes cluster configurations compared
- [ ] Docker image in ECR
- [ ] Helm chart working

## 🔧 Common Issues & Fixes

### Issue: Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Common fixes:
# - Verify image exists in ECR
# - Check ECR authentication
# - Review resource limits
```

### Issue: ImagePullBackOff

```bash
# Verify ECR repository
aws ecr describe-repositories --repository-name qr-service

# Update image pull policy
helm upgrade qr-code-service ./helm \
  --set qrService.image.pullPolicy=Always
```

### Issue: Can't access service

```bash
# Check service type is LoadBalancer
kubectl get service qr-service

# Verify security groups allow traffic
# Check AWS console for ELB

# Try NodePort as alternative:
helm upgrade qr-code-service ./helm \
  --set qrService.service.type=NodePort
```

### Issue: Authentication failing

```bash
# Check auth service is running
kubectl get pods -l app=auth-service

# Check auth service logs
kubectl logs -l app=auth-service

# Verify service DNS
kubectl exec -it <qr-pod> -- nslookup auth-service
```

## 📈 Scaling Options

### Manual Scaling

```bash
# Scale to 10 replicas
kubectl scale deployment qr-service --replicas=10

# Or with Helm
helm upgrade qr-code-service ./helm \
  --set qrService.replicaCount=10
```

### Adjust HPA

```bash
# Edit values.yaml
# qrService.autoscaling.minReplicas: 5
# qrService.autoscaling.maxReplicas: 20

helm upgrade qr-code-service ./helm
```

### Change Instance Resources

```bash
# Edit values.yaml
# qrService.resources.limits.cpu: "1000m"
# qrService.resources.limits.memory: "1Gi"

helm upgrade qr-code-service ./helm
```

## 🔄 Update & Rollback

### Update Code

```bash
# Make changes, rebuild
docker build -t qr-service:v1.0.1 .
./build-and-push.sh

# Update values.yaml with new tag
# Deploy update
helm upgrade qr-code-service ./helm
```

### Rollback

```bash
# View history
helm history qr-code-service

# Rollback to previous
helm rollback qr-code-service
```

## 🧹 Cleanup

```bash
# Uninstall Helm release
helm uninstall qr-code-service

# Delete namespace (if used)
kubectl delete namespace qr-service

# Delete ECR repository
aws ecr delete-repository \
  --repository-name qr-service \
  --force \
  --region us-east-1
```

## 📚 Next Steps

1. **Read DEPLOYMENT.md** for detailed deployment guide
2. **Read README.md** for architecture and API details
3. **Configure monitoring** (Prometheus, Grafana)
4. **Set up CI/CD** pipeline
5. **Implement second framework** for comparison
6. **Test different load balancers**
7. **Optimize cluster configuration**

## 🆘 Getting Help

- Check logs: `kubectl logs <pod-name>`
- Describe resources: `kubectl describe <resource> <name>`
- Review Helm values: `helm get values qr-code-service`
- See full documentation in README.md and DEPLOYMENT.md

Good luck with your QR Code Service! 🎉
