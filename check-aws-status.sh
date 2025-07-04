#!/bin/bash

echo "🔍 Checking AWS Resources Status..."
echo "================================="

# Check Database Stack
echo "📊 Database Stack Status:"
DB_STATUS=$(aws cloudformation describe-stacks --stack-name forecast-my-park-db --region us-east-1 --query 'Stacks[0].StackStatus' --output text 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   Status: $DB_STATUS"
    
    if [ "$DB_STATUS" = "CREATE_COMPLETE" ]; then
        echo "   ✅ Database is ready!"
        DB_ENDPOINT=$(aws cloudformation describe-stacks --stack-name forecast-my-park-db --region us-east-1 --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' --output text 2>/dev/null)
        echo "   📍 Database Endpoint: $DB_ENDPOINT"
        echo ""
        echo "🔧 Update your aws.env file with:"
        echo "   POSTGRES_HOST=$DB_ENDPOINT"
        echo "   POSTGRES_PORT=5432"
        echo "   POSTGRES_DB=postgres"
        echo "   POSTGRES_USER=postgres"
        echo "   POSTGRES_PASSWORD=forecast123!"
    elif [ "$DB_STATUS" = "ROLLBACK_COMPLETE" ] || [ "$DB_STATUS" = "CREATE_FAILED" ]; then
        echo "   ❌ Database creation failed!"
        echo "   Check CloudFormation console for details"
    else
        echo "   ⏳ Database is still being created..."
    fi
else
    echo "   ❌ Database stack not found"
fi

echo ""

# Check ECS Cluster
echo "🖥️  ECS Cluster Status:"
ECS_STATUS=$(aws cloudformation describe-stacks --stack-name forecast-my-park-minimal --region us-east-1 --query 'Stacks[0].StackStatus' --output text 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   Status: $ECS_STATUS"
    if [ "$ECS_STATUS" = "CREATE_COMPLETE" ]; then
        echo "   ✅ ECS Cluster is ready!"
    fi
else
    echo "   ❌ ECS Cluster not found"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Create EC2 instance via AWS Console (see AWS_DEPLOYMENT_GUIDE.md)"
echo "2. Once database is ready, use the endpoint in your aws.env file"
echo "3. Deploy your application with: docker-compose -f docker-compose.aws.yml --env-file aws.env up -d"
echo ""
echo "Run this script again to check updated status!" 