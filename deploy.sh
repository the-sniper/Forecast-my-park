#!/bin/bash

# Forecast My Park - AWS Deployment Script
set -e

echo "Starting deployment to AWS..."

# Configuration
PROJECT_NAME="forecast-my-park"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REPO_PREFIX="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# Check required environment variables
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "Error: AWS_ACCOUNT_ID environment variable is required"
    exit 1
fi

# Get AWS account ID if not set
if [ -z "$AWS_ACCOUNT_ID" ]; then
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
fi

echo "Using AWS Account: $AWS_ACCOUNT_ID"
echo "Using AWS Region: $AWS_REGION"

# Authenticate Docker to ECR
echo "Authenticating with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_PREFIX

# Create ECR repositories if they don't exist
echo "Creating ECR repositories..."
aws ecr describe-repositories --repository-names "${PROJECT_NAME}-frontend" --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name "${PROJECT_NAME}-frontend" --region $AWS_REGION

aws ecr describe-repositories --repository-names "${PROJECT_NAME}-ml-service" --region $AWS_REGION 2>/dev/null || \
    aws ecr create-repository --repository-name "${PROJECT_NAME}-ml-service" --region $AWS_REGION

# Build and push frontend
echo "Building frontend image..."
docker build -t "${PROJECT_NAME}-frontend" ./frontend
docker tag "${PROJECT_NAME}-frontend:latest" "${ECR_REPO_PREFIX}/${PROJECT_NAME}-frontend:latest"
docker push "${ECR_REPO_PREFIX}/${PROJECT_NAME}-frontend:latest"

# Build and push ML service
echo "Building ML service image..."
docker build -t "${PROJECT_NAME}-ml-service" ./ml-service
docker tag "${PROJECT_NAME}-ml-service:latest" "${ECR_REPO_PREFIX}/${PROJECT_NAME}-ml-service:latest"
docker push "${ECR_REPO_PREFIX}/${PROJECT_NAME}-ml-service:latest"

echo "Images pushed to ECR successfully!"

# Deploy to ECS (if task definitions exist)
if aws ecs describe-task-definition --task-definition "${PROJECT_NAME}-frontend" --region $AWS_REGION 2>/dev/null; then
    echo "Updating ECS services..."
    aws ecs update-service --cluster "${PROJECT_NAME}-cluster" --service "${PROJECT_NAME}-frontend" --force-new-deployment --region $AWS_REGION
    aws ecs update-service --cluster "${PROJECT_NAME}-cluster" --service "${PROJECT_NAME}-ml-service" --force-new-deployment --region $AWS_REGION
    echo "ECS services updated!"
else
    echo "ECS task definitions not found. Please set up ECS infrastructure first."
fi

echo "🎉 Deployment completed!" 