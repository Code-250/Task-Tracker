#!/bin/bash
# Script to build and push Docker image to ECR

set -e

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-587764054854}
REPO_NAME=${REPO_NAME:-qr-service}
IMAGE_TAG=${IMAGE_TAG:-latest}

echo "=========================================="
echo "QR Code Service - Build and Push to ECR"
echo "=========================================="
echo "AWS Region: $AWS_REGION"
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "Repository: $REPO_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "=========================================="

# Build Docker image
echo ""
echo "Step 1: Building Docker image..."
docker build -t ${REPO_NAME}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    echo "✓ Docker build successful"
else
    echo "✗ Docker build failed"
    exit 1
fi

# Authenticate to ECR
echo ""
echo "Step 2: Authenticating to Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

if [ $? -eq 0 ]; then
    echo "✓ ECR authentication successful"
else
    echo "✗ ECR authentication failed"
    exit 1
fi

# Create repository if it doesn't exist
echo ""
echo "Step 3: Ensuring ECR repository exists..."
aws ecr describe-repositories --repository-names ${REPO_NAME} --region ${AWS_REGION} > /dev/null 2>&1 || \
    aws ecr create-repository \
        --repository-name ${REPO_NAME} \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true

if [ $? -eq 0 ]; then
    echo "✓ Repository ready"
else
    echo "✗ Repository creation failed"
    exit 1
fi

# Tag image
echo ""
echo "Step 4: Tagging image..."
docker tag ${REPO_NAME}:${IMAGE_TAG} \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}

echo "✓ Image tagged"

# Push to ECR
echo ""
echo "Step 5: Pushing to ECR..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}

if [ $? -eq 0 ]; then
    echo "✓ Push successful"
else
    echo "✗ Push failed"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "✓ Build and push completed successfully!"
echo "=========================================="
echo ""
echo "Image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}:${IMAGE_TAG}"
echo ""
echo "Next steps:"
echo "  1. Update helm/values.yaml with the image tag"
echo "  2. Deploy with: helm install qr-code-service ./helm"
echo ""
