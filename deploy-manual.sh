#!/bin/bash

# Manual AWS Deployment Script for Forecast My Park
set -e

echo "🚀 Starting AWS Deployment for Forecast My Park"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Run 'aws configure' first."
    exit 1
fi

# Set variables
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=${AWS_REGION:-us-east-1}
export PROJECT_NAME="forecast-my-park"

echo "📋 AWS Account ID: $AWS_ACCOUNT_ID"
echo "📋 AWS Region: $AWS_REGION"

# Step 1: Deploy Infrastructure
echo "🏗️ Step 1: Deploying Infrastructure..."
aws cloudformation create-stack \
  --stack-name forecast-my-park-infra \
  --template-body file://aws-infrastructure/cloudformation-template.yml \
  --parameters ParameterKey=DBPassword,ParameterValue=ForecastMyPark2024! \
  --capabilities CAPABILITY_IAM \
  --region $AWS_REGION

echo "⏳ Waiting for infrastructure deployment (this may take 5-10 minutes)..."
aws cloudformation wait stack-create-complete \
  --stack-name forecast-my-park-infra \
  --region $AWS_REGION

# Step 2: Get Infrastructure Outputs
echo "📊 Getting infrastructure details..."
DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name forecast-my-park-infra \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text \
  --region $AWS_REGION)

ALB_DNS=$(aws cloudformation describe-stacks \
  --stack-name forecast-my-park-infra \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text \
  --region $AWS_REGION)

echo "🗄️ Database Endpoint: $DB_ENDPOINT"
echo "🌐 Load Balancer: $ALB_DNS"

# Step 3: Create ECR Repositories
echo "📦 Step 3: Creating ECR repositories..."
aws ecr create-repository \
  --repository-name ${PROJECT_NAME}-frontend \
  --region $AWS_REGION 2>/dev/null || echo "Frontend repo already exists"

aws ecr create-repository \
  --repository-name ${PROJECT_NAME}-ml-service \
  --region $AWS_REGION 2>/dev/null || echo "ML service repo already exists"

aws ecr create-repository \
  --repository-name ${PROJECT_NAME}-data-loader \
  --region $AWS_REGION 2>/dev/null || echo "Data loader repo already exists"

# Step 4: Authenticate Docker to ECR
echo "🔐 Step 4: Authenticating Docker with ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Step 5: Build and Push Images
echo "🏗️ Step 5: Building and pushing Docker images..."

# Build and push frontend
echo "📦 Building frontend..."
docker build -t ${PROJECT_NAME}-frontend ./frontend
docker tag ${PROJECT_NAME}-frontend:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-frontend:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-frontend:latest

# Build and push ML service
echo "📦 Building ML service..."
docker build -t ${PROJECT_NAME}-ml-service ./ml-service
docker tag ${PROJECT_NAME}-ml-service:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-ml-service:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-ml-service:latest

# Build and push data loader
echo "📦 Building data loader..."
docker build -t ${PROJECT_NAME}-data-loader ./data-scripts
docker tag ${PROJECT_NAME}-data-loader:latest \
  ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-data-loader:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-data-loader:latest

# Step 6: Update ECS Task Definitions
echo "📝 Step 6: Creating ECS task definitions..."

# Update task definition with real values
sed "s/YOUR_ACCOUNT_ID/${AWS_ACCOUNT_ID}/g; s/your-rds-endpoint.amazonaws.com/${DB_ENDPOINT}/g" \
  aws-infrastructure/ecs-task-definitions.json > /tmp/task-definitions-updated.json

# Register task definitions
aws ecs register-task-definition \
  --cli-input-json file:///tmp/task-definitions-updated.json \
  --region $AWS_REGION

echo "✅ Deployment completed!"
echo ""
echo "🌐 Your application will be available at: http://$ALB_DNS"
echo "🗄️ Database endpoint: $DB_ENDPOINT"
echo ""
echo "Next steps:"
echo "1. Create ECS services in the AWS Console"
echo "2. Configure Application Load Balancer routing"
echo "3. Set up domain name (optional)" 