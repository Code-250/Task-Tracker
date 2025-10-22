# QR Code Service - Deployment Guide

## Prerequisites

### Required Tools
- AWS CLI configured with your credentials
- Docker installed and running
- kubectl configured to access your EKS cluster
- Helm 3 installed
- Python 3.11+ (for local testing)

### AWS Resources
- EKS cluster provisioned
- ECR repository created
- Appropriate IAM roles and permissions

## Step-by-Step Deployment

### Step 1: Build and Test Locally

```bash
# Navigate to project directory
cd qr-service

# Install dependencies
pip install -r requirements.txt

# Run locally for testing
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Test in another terminal
curl "http://localhost:8080/qrcode?type=encode&data=Hello"
```

### Step 2: Build Docker Image

```bash
# Build the image
docker build -t qr-service:v1.0.0 .

# Test the Docker image locally
docker run -p 8080:8080 \
  -e TEAM_NAME=Cumulonimbus \
  -e TEAM_AWS_ID=587764054854 \
  qr-service:v1.0.0

# Test
curl "http://localhost:8080/qrcode?type=encode&data=Hello"
```

### Step 3: Push to Amazon ECR

```bash
# Set variables
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=587764054854
REPO_NAME=qr-service
IMAGE_TAG=v1.0.0

# Authenticate Docker to ECR
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Create repository (first time only)
aws ecr create-repository \
  --repository-name $REPO_NAME \
  --region $AWS_REGION \
  --image-scanning-configuration scanOnPush=true

# Tag image
docker tag qr-service:${IMAGE_TAG} \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}

docker tag qr-service:${IMAGE_TAG} \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:latest

# Push to ECR
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:latest
```

### Step 4: Configure Kubernetes Cluster

```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Create namespace (optional)
kubectl create namespace qr-service

# Set context to namespace
kubectl config set-context --current --namespace=qr-service
```

### Step 5: Configure Helm Values

Edit `helm/values.yaml`:

```yaml
qrService:
  image:
    repository: 587764054854.dkr.ecr.us-east-1.amazonaws.com/qr-service
    tag: "v1.0.0"  # or "latest"

  replicaCount: 3  # Adjust based on expected load

  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"

authService:
  image:
    tag: "amd64"  # Change to "arm64" if using ARM instances
```

### Step 6: Deploy with Helm

```bash
# Dry run to check templates
helm install qr-code-service ./helm --dry-run --debug

# Install the chart
helm install qr-code-service ./helm

# Or with custom namespace
helm install qr-code-service ./helm --namespace qr-service --create-namespace

# Check deployment status
kubectl get all
kubectl get pods -w  # Watch pods starting

# Check logs
kubectl logs -l app=qr-service
kubectl logs -l app=auth-service
```

### Step 7: Verify Deployment

```bash
# Check pods are running
kubectl get pods

# Check services
kubectl get services

# Get external IP/hostname (for LoadBalancer)
kubectl get service qr-service
# Wait for EXTERNAL-IP to be assigned (may take a few minutes)

# Test the service
EXTERNAL_IP=$(kubectl get service qr-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl "http://${EXTERNAL_IP}/qrcode?type=encode&data=Hello"
```

### Step 8: Configure Autoscaling

The HPA (Horizontal Pod Autoscaler) is deployed automatically. Monitor it:

```bash
# Check HPA status
kubectl get hpa

# Describe HPA for details
kubectl describe hpa qr-service-hpa

# Watch autoscaling in action
kubectl get hpa -w
```

## Performance Testing

### Prepare for Load Testing

1. **Configure Sail() Load Generator** with your service endpoint
2. **Monitor metrics** during testing:

```bash
# Watch pod count
kubectl get pods -l app=qr-service -w

# Monitor resource usage
kubectl top pods
kubectl top nodes

# View HPA metrics
kubectl get hpa -w
```

3. **Run 600-second test** to meet full score requirements

### Performance Tuning

#### Increase Replicas
```bash
helm upgrade qr-code-service ./helm --set qrService.replicaCount=10
```

#### Adjust Resources
```bash
# Edit values.yaml, then:
helm upgrade qr-code-service ./helm
```

#### Change Instance Type
```bash
# Modify EKS node group to use different instance types
# Then redeploy pods to new nodes
kubectl rollout restart deployment qr-service
```

## Framework Comparison

To compare different frameworks, create separate implementations:

### FastAPI (Current)
- Already implemented

### Flask
```bash
# Create separate helm values for Flask version
helm install qr-flask ./helm-flask --set qrService.image.tag=flask-v1.0.0
```

### Go (Gin)
```bash
# Build Go version, push to ECR with different tag
helm install qr-go ./helm --set qrService.image.tag=go-v1.0.0
```

## Load Balancer Comparison

### AWS ALB (Default)
Already configured in helm chart with LoadBalancer service type.

### AWS NLB
```yaml
# In helm/values.yaml
qrService:
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
```

### NGINX Ingress Controller

```bash
# Install NGINX Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx

# Enable ingress in values.yaml
ingress:
  enabled: true
  className: "nginx"

# Change service type to ClusterIP
qrService:
  service:
    type: ClusterIP

# Upgrade deployment
helm upgrade qr-code-service ./helm
```

## Monitoring and Debugging

### View Logs
```bash
# Application logs
kubectl logs -f deployment/qr-service

# Auth service logs
kubectl logs -f deployment/auth-service

# All pods
kubectl logs -l app=qr-service --tail=100 -f
```

### Debug Pod Issues
```bash
# Describe pod for events
kubectl describe pod <pod-name>

# Execute shell in pod
kubectl exec -it <pod-name> -- /bin/bash

# Check environment variables
kubectl exec <pod-name> -- env

# Test DNS resolution
kubectl exec <pod-name> -- nslookup auth-service
```

### Check Resource Usage
```bash
# Install metrics server if not present
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View metrics
kubectl top nodes
kubectl top pods
```

## Updating the Deployment

### Update Application Code
```bash
# Make code changes
# Build new image with new tag
docker build -t qr-service:v1.0.1 .

# Push to ECR
docker tag qr-service:v1.0.1 \
  587764054854.dkr.ecr.us-east-1.amazonaws.com/qr-service:v1.0.1
docker push 587764054854.dkr.ecr.us-east-1.amazonaws.com/qr-service:v1.0.1

# Update values.yaml with new tag
# Upgrade Helm release
helm upgrade qr-code-service ./helm

# Or force pod restart
kubectl rollout restart deployment qr-service
```

### Rollback
```bash
# View revision history
helm history qr-code-service

# Rollback to previous version
helm rollback qr-code-service

# Rollback to specific revision
helm rollback qr-code-service 2
```

## Cleanup

### Uninstall Helm Chart
```bash
helm uninstall qr-code-service
```

### Delete Namespace
```bash
kubectl delete namespace qr-service
```

### Delete ECR Images
```bash
aws ecr batch-delete-image \
  --repository-name qr-service \
  --image-ids imageTag=v1.0.0 \
  --region us-east-1
```

## Troubleshooting

### Pods in CrashLoopBackOff
```bash
kubectl logs <pod-name> --previous
kubectl describe pod <pod-name>
```

### ImagePullBackOff
- Verify ECR authentication
- Check image name and tag
- Ensure cluster has permissions to pull from ECR

### Auth Service Connection Issues
```bash
# Check auth service is running
kubectl get pods -l app=auth-service

# Test connectivity from qr-service pod
kubectl exec -it <qr-pod> -- curl http://auth-service:9000
```

### Performance Issues
- Check HPA is working: `kubectl get hpa`
- Verify resource limits aren't too restrictive
- Monitor node capacity: `kubectl top nodes`
- Check for throttling in application logs

## Best Practices

1. **Use specific image tags** (not `latest`) for production
2. **Set resource limits** to prevent resource exhaustion
3. **Enable autoscaling** for variable load
4. **Monitor logs** during load testing
5. **Test rollback procedures** before production
6. **Use health checks** for pod readiness
7. **Keep Helm values** in version control
8. **Document cluster configuration** for reports

## Report Checklist

Ensure you collect data for the report:

- [ ] 600-second Sail() submission reaching target throughput
- [ ] Performance comparison of ≥2 frameworks
- [ ] Kubernetes cluster configuration comparison (instance types & numbers)
- [ ] Docker image in ECR with Dockerfile in code submission
- [ ] Helm chart that deploys complete service
- [ ] Load balancer performance comparison (optional but encouraged)
- [ ] Screenshots/metrics of performance tests
- [ ] Analysis of bottlenecks and optimizations

## Support

For issues:
1. Check logs: `kubectl logs`
2. Review pod events: `kubectl describe pod`
3. Verify configuration: `helm get values qr-code-service`
4. Test components individually
5. Review README.md and this guide

Good luck with your deployment and performance testing!
